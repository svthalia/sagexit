from django.contrib.auth import get_user_model
from django.db import models


class Room(models.Model):
    """Model for a Room that can be reserved."""

    name = models.CharField(max_length=200)
    capacity = models.SmallIntegerField(blank=False, null=False)

    def __str__(self):
        """Return small description about the room."""
        return f"{self.name} (max. {self.capacity}p)"


class Reservation(models.Model):
    """Model for a reservation that is made by a reservee for a certain room, with an start and end date."""

    reservee = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    block_whole_room = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        """Return small description about the reservation."""
        return f"{self.reservee} has {self.room} reserved at {self.start_time} until {self.end_time}"
