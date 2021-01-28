from django import forms
from urllib.parse import quote


class LoginForm(forms.Form):

    username = forms.CharField(label="Science username")
    remember = forms.BooleanField(label="Remember username", initial=True, required=False)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return quote(username.lower())
