import datetime

import pytz
from django.apps import AppConfig

__author__ = 'abolfazl'


class MainConfig(AppConfig):
    name = "main"
    verbose_name = "main"

    def ready(self):
        from Signals import authentication_signals
        pass


def jwt_response_payload_handler11(token, user=None, request=None):
    if user and request:
        user.last_login = datetime.datetime.now(tz=pytz.utc)
        user.save()
    return {
        'token': token,
    }
