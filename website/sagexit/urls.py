from django.contrib import admin, auth
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import RedirectView


def logout(request):
    auth.logout(request)
    return redirect("/")


urlpatterns = [
    path("", RedirectView.as_view(url="/reservations")),
    path("reservations/", include("room_reservation.urls")),
    path("admin/", admin.site.urls),
    path("logout/", logout, name="logout"),
    path("sso/", include("sp.urls")),
]
