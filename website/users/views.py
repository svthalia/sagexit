from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import LoginForm
from .services import get_openid_verifier


class LoginView(TemplateView):

    template_name = "users/login.html"

    remember_cookie = "_remembered_username"

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            else:
                return redirect("/")

        form = LoginForm()
        remembered_username = request.COOKIES.get(self.remember_cookie, None)
        if remembered_username is not None:
            form.fields["username"].initial = remembered_username

        return render(request, self.template_name, {"form": form})

    def post(self, request, **kwargs):
        form = LoginForm(request.POST)

        if request.user.is_authenticated:
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            else:
                return redirect("/")

        if form.is_valid():
            openid_verifier = get_openid_verifier(request)
            verify_url = openid_verifier.get_request_url(
                form.cleaned_data.get("username")
            )
            response = redirect(verify_url)
            if form.cleaned_data.get("remember"):
                response.set_cookie(
                    self.remember_cookie, form.cleaned_data.get("username")
                )
            return response

        return render(request, self.template_name, {"form": form})


class VerifyView(TemplateView):

    template_name = "users/verify.html"

    def get(self, request, **kwargs):
        openid_verifier = get_openid_verifier(request)
        user, created = openid_verifier.extract_user()
        if user:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            next_page = request.GET.get("next")
            if next_page:
                return redirect(next_page)
            return redirect("/")

        return render(request, self.template_name)


class LogoutView(TemplateView):

    template_name = "users/logout.html"

    def get(self, request, **kwargs):
        next_page = request.GET.get("next")
        if request.user.is_authenticated:
            logout(request)
            if next_page:
                return redirect(next_page)
            return render(request, self.template_name)
        else:
            if next_page:
                return redirect(next_page)
            return redirect("/")
