from django.apps import AppConfig

__author__ = 'abolfazl'


class AdminConfig(AppConfig):
    name = "admin"
    verbose_name = "admin"

    def ready(self):
        from Signals import models_signals
        pass
