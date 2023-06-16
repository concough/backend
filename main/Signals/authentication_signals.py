from django.contrib.auth import user_logged_in
from django.dispatch.dispatcher import receiver

__author__ = 'abolfazl'


@receiver(user_logged_in)
def after_user_logged_in(sender, user, request, **kwargs):
    pass
