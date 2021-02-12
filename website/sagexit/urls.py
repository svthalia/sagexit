from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import saml2_pro_auth.urls as saml_urls

urlpatterns = [
    path("", RedirectView.as_view(url="/reservations")),
    path("reservations/", include("room_reservation.urls")),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("sso/saml/", include(saml_urls, namespace="saml")),
]
