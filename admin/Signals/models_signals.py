from django.db import models
from main.models import EntranceQuestionImages

__author__ = 'abolfazl'


def post_delete_question_image(sender, instance, **kwargs):
    if isinstance(instance, EntranceQuestionImages):
        storage, path = instance.image.storage, instance.image.path
        storage.delete(path)

models.signals.post_delete.connect(post_delete_question_image, sender=EntranceQuestionImages)
