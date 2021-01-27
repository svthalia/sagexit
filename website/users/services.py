from urllib.parse import urlencode, urlparse, parse_qsl
import requests
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse


def get_openid_verifier(request):
    return_url = request.build_absolute_uri(reverse(settings.OPENID_RETURN_URL))

    next_page = request.GET.get("next")
    if next_page:
        params = urlencode({"next": next_page})
        return_url += "?" + params

    return OpenIDVerifier(
        settings.OPENID_SERVER_ENDPOINT,
        request,
        return_url,
        settings.OPENID_USERNAME_PREFIX,
        settings.OPENID_USERNAME_POSTFIX,
    )


class OpenIDVerifier:
    def __init__(
        self, openid_server_endpoint, request, openid_return_url, prefix, postfix
    ):
        self.openid_server_endpoint = openid_server_endpoint
        self.openid_trust_root = request.META["HTTP_HOST"]
        self.openid_return_url = openid_return_url
        self.prefix = prefix
        self.postfix = postfix
        self.request = request
        self.query_parameters = dict(parse_qsl(urlparse(request.get_full_path()).query))
        self.signed_field_values = dict()
        if "openid.signed" in self.query_parameters.keys():
            for field in self.query_parameters["openid.signed"].split(","):
                if field != "mode":
                    self.signed_field_values[
                        "openid.{}".format(field)
                    ] = self.query_parameters["openid.{}".format(field)]

    def get_request_url(self, username):
        parameters = {
            "openid.mode": "checkid_setup",
            "openid.sreg.required": "fullname,email",
            "openid.identity": self.get_full_user_id(username),
            "openid.return_to": self.openid_return_url,
            "openid.trust_root": self.openid_trust_root,
        }
        return "{}?{}".format(self.openid_server_endpoint, urlencode(parameters))

    def get_full_user_id(self, username):
        return "{}{}{}".format(self.prefix, username, self.postfix)

    def extract_username(self):
        if "openid.identity" in self.query_parameters.keys():
            openid_identity = self.query_parameters["openid.identity"]
            return re.sub(
                "{}$".format(self.postfix),
                "",
                re.sub("^{}".format(self.prefix), "", openid_identity),
            )
        return False

    def extract_full_name(self):
        if "openid.sreg.fullname" in self.query_parameters.keys():
            return self.query_parameters["openid.sreg.fullname"]
        return False

    def extract_email_address(self):
        if "openid.sreg.email" in self.query_parameters.keys():
            return self.query_parameters["openid.sreg.email"]
        return False

    def get_verification_url(self):
        keys = self.query_parameters.keys()
        if not (
            "openid.mode" in keys
            and "openid.assoc_handle" in keys
            and "openid.sig" in keys
            and "openid.signed" in keys
        ):
            return False

        parameters = {
            "openid.mode": "check_authentication",
            "openid.assoc_handle": self.query_parameters["openid.assoc_handle"],
            "openid.sig": self.query_parameters["openid.sig"],
            "openid.signed": self.query_parameters["openid.signed"],
        }

        parameters = {**parameters, **self.signed_field_values}

        return "{}?{}".format(self.openid_server_endpoint, urlencode(parameters))

    def verify_request(self):
        return (
            "openid.mode" in self.query_parameters.keys()
            and self.query_parameters["openid.mode"] == "id_res"
            and self.verify_signature()
        )

    def verify_signature(self):
        verification_url = self.get_verification_url()
        response = requests.get(verification_url)
        return (
            response.status_code == 200
            and re.sub("is_valid:", "", re.sub("\n", "", response.text)) == "true"
        )

    def set_user_details(self, user):
        full_name = self.extract_full_name()
        email = self.extract_email_address()

        if full_name:
            user.first_name = full_name.split(" ", 1)[0]
            user.last_name = full_name.split(" ", 1)[1]

        if email:
            user.email = email

        user.save()

    def extract_user(self):
        if self.verify_request():
            username = self.extract_username()
            if username:
                user, created = get_user_model().objects.get_or_create(
                    username=username
                )
                if created:
                    self.set_user_details(user)
                return user, created
        return None, False
