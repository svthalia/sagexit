from django.urls import path

from .views import CreateReservationView
from .views import DeleteReservationView
from .views import ShowCalendarView
from .views import UpdateReservationView

app_name = "room_reservation"

urlpatterns = [
    path("", ShowCalendarView.as_view(), name="calendar"),
    path("create", CreateReservationView.as_view(), name="create_reservation"),
    path("<int:pk>/update", UpdateReservationView.as_view(), name="update_reservation"),
    path("<int:pk>/delete", DeleteReservationView.as_view(), name="delete_reservation"),
]
