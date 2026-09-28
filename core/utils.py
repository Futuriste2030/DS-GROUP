from email.utils import formataddr
from django.conf import settings


def sender_address(name=None):
    display = name or getattr(settings, 'EMAIL_FROM_NAME', 'BS GROUP')
    return formataddr((display, settings.DEFAULT_FROM_EMAIL))
