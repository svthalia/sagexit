from django.contrib import admin
from django.urls import path
from .views import LoginView, VerifyView, LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("verify/", VerifyView.as_view(), name="verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

admin.autodiscover()
admin.site.login = LoginView.as_view()
admin.site.logout = LogoutView.as_view()
