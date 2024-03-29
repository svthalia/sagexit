import json
from datetime import timedelta
from json import JSONDecodeError

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import dateparse, timezone
from django.views import View
from django.views.generic import TemplateView

from .models import Reservation, Room


class BaseReservationView(View):
    """Base class for reservation API endpoints."""

    def validate(self, room, start_time, end_time, pk=None, user=None):
        """
        Validate the input for the reservation.

        By checking:

        - All checks made by ModelForm.
        - Reservation does not collide with another reservation.
        - Reservation is not too long.
        """
        start_time = start_time.astimezone(timezone.get_current_timezone())
        end_time = end_time.astimezone(timezone.get_current_timezone())

        if end_time.date() > timezone.now().date() + timezone.timedelta(weeks=1):
            return False, "You can only make reservation 1 week in advance"

        if end_time.date() - start_time.date() >= timezone.timedelta(days=1):
            return False, "Reservation too long. Please shorten your reservation"

        if start_time >= end_time:
            return False, "Start time needs to be before end time"

        if start_time.hour < 8 or start_time.hour >= 18 or end_time.hour < 8 or end_time.hour >= 18:
            return False, "Please enter times between 8:00 and 18:00"

        if start_time.weekday() in (5, 6):
            return False, "Rooms cannot be reserved in the weekends"

        overlapping_same_user = (
            Reservation.objects.filter(reservee=user)
            .filter(
                Q(start_time__lte=start_time, end_time__gt=start_time)
                | Q(start_time__lt=end_time, end_time__gte=end_time)
                | Q(start_time__gte=start_time, end_time__lte=end_time)
            )
            .exclude(pk=pk)
        )

        if overlapping_same_user.count() >= 1:
            return False, "You cannot reserve multiple rooms"

        overlapping_reservations = (
            Reservation.objects.filter(room=room)
            .filter(
                Q(start_time__lte=start_time, end_time__gt=start_time)
                | Q(start_time__lt=end_time, end_time__gte=end_time)
                | Q(start_time__gte=start_time, end_time__lte=end_time)
            )
            .exclude(pk=pk)
        )

        if overlapping_reservations.filter(block_whole_room=True).exists():
            return False, "This room is blocked."

        start_times = sorted(overlapping_reservations.values_list("start_time"))
        end_times = sorted(overlapping_reservations.values_list("end_time"))

        i = 1
        j = 0

        simultaneous = 1
        max_overlapping = 1
        while i < len(start_times) and j < len(start_times):
            if start_times[i] < end_times[j]:
                simultaneous += 1
                if simultaneous > max_overlapping:
                    max_overlapping = simultaneous
                i += 1
            else:
                simultaneous -= 1
                j += 1

        capacity_reached = max_overlapping >= Room.objects.get(id=room).capacity

        if capacity_reached:
            return False, "Capacity is reached for this room"
        return True, None

    def load_json(self):
        """Extract the json data from text_body."""
        body = json.loads(self.request.body)
        room = body["room"]
        start_time = dateparse.parse_datetime(body["start_time"])
        end_time = dateparse.parse_datetime(body["end_time"])
        return room, start_time, end_time

    def can_edit(self, reservation):
        """Return true if the reservation can be edited by the logged in user."""
        return self.request.user == reservation.reservee


class ShowCalendarView(TemplateView, BaseReservationView):
    """
    Show a week-calendar and showing the current reservations.

    From here, it is possible to make reservations,
    and to update and delete your own.
    """

    template_name = "room_reservation/index.html"

    def get_context_data(self, **kwargs):
        """Load all information for the calendar."""
        context = super(ShowCalendarView, self).get_context_data(**kwargs)

        context["reservations"] = json.dumps(
            [
                {
                    "pk": reservation.pk,
                    "title": f"{reservation.reservee.get_full_name()} ({reservation.room.name})"
                    if not reservation.block_whole_room
                    else f"{reservation.room.name} BLOCKED",
                    "reservee": reservation.reservee.get_full_name(),
                    "room": reservation.room_id,
                    "start": reservation.start_time.isoformat(),
                    "end": reservation.end_time.isoformat(),
                    "editable": self.can_edit(reservation),
                }
                for reservation in Reservation.objects.filter(
                    start_time__date__gte=timezone.now() - timedelta(days=60),
                    start_time__date__lt=timezone.now() + timedelta(days=60),
                )
            ]
        )
        context["rooms"] = Room.objects.all()
        return context


class CreateReservationView(LoginRequiredMixin, BaseReservationView):
    """View to make a reservation."""

    raise_exception = True

    def post(self, request, *args, **kwargs):
        """Handle the POST method for this view."""
        try:
            room, start_time, end_time = self.load_json()
        except (KeyError, JSONDecodeError):
            return HttpResponseBadRequest(json.dumps({"ok": "False", "message": "Bad request"}))

        ok, message = self.validate(room, start_time, end_time, user=self.request.user)
        if not ok:
            return JsonResponse({"ok": False, "message": message})

        if start_time < timezone.now():
            return JsonResponse({"ok": False, "message": "You cannot make reservations in the past"})

        reservation = Reservation.objects.create(
            reservee=request.user,
            room_id=room,
            start_time=start_time,
            end_time=end_time,
        )
        return JsonResponse({"ok": True, "pk": reservation.pk})


class UpdateReservationView(LoginRequiredMixin, BaseReservationView):
    """View to update your reservation."""

    raise_exception = True

    def post(self, request, pk, *args, **kwargs):
        """Handle the POST method for this view."""
        try:
            room, start_time, end_time = self.load_json()
        except (KeyError, JSONDecodeError):
            return HttpResponseBadRequest(json.dumps({"ok": "False", "message": "Bad request"}))

        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return JsonResponse({"ok": False, "message": "This reservation does not exist"})

        if not self.can_edit(reservation):
            return JsonResponse({"ok": False, "message": "You can only update your own events"})

        # If the event took place in the past
        if reservation.start_time < reservation.end_time < timezone.now():
            if reservation.start_time == start_time and end_time > timezone.now():  # We can only extend the end time
                pass
            else:
                return JsonResponse({"ok": False, "message": "You cannot update events from the past"})

        # If the event is active
        if reservation.start_time < timezone.now() < reservation.end_time:
            if (
                reservation.start_time == start_time and end_time > timezone.now()
            ):  # We can only change the end time to the future
                pass
            else:
                return JsonResponse({"ok": False, "message": "You cannot change the start or end time to this value"})

        # If the event is in the future
        if timezone.now() < reservation.start_time < reservation.end_time:
            if start_time < timezone.now():  # We cannot change the start time to the past
                return JsonResponse({"ok": False, "message": "You cannot change the start time to this value"})

        ok, message = self.validate(room, start_time, end_time, pk=pk, user=self.request.user)
        if not ok:
            return JsonResponse({"ok": False, "message": message})

        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.save()
        return JsonResponse({"ok": True})


class DeleteReservationView(LoginRequiredMixin, BaseReservationView):
    """View to delete your reservation."""

    raise_exception = True

    def post(self, request, pk, *args, **kwargs):
        """Handle the POST method for this view."""
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return JsonResponse({"ok": False, "message": "This reservation does not exist"})

        if not self.can_edit(reservation):
            return JsonResponse({"ok": False, "message": "You can only delete your own events"})

        if reservation.start_time < reservation.end_time < timezone.now():
            return JsonResponse({"ok": False, "message": "You cannot remove events from the past"})

        if reservation.start_time < timezone.now() < reservation.end_time:
            return JsonResponse({"ok": False, "message": "You cannot remove this active event"})

        reservation.delete()
        return JsonResponse({"ok": True})
