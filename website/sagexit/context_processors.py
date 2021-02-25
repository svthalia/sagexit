from django.conf import settings  # import the settings file
from sp.models import IdP


def default_sso(request):
    """Context processor for the default SSO object"""
    try:
        return {"DEFAULT_SSO": IdP.objects.get(slug=settings.DEFAULT_SSO_SLUG)}
    except AttributeError:
        return {"DEFAULT_SSO": IdP.objects.filter(is_active=True).first()}
