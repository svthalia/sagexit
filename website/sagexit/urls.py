import django_saml2_auth
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/reservations")),
    path("reservations/", include("room_reservation.urls")),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("saml2_auth/", include("django_saml2_auth.urls")),
    path("saml2_auth/login/", django_saml2_auth.views.signin),
]
