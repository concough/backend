from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from dataentry.models import Task, ReadyData
from main.Forms.FormHelpers import error_messages
from main.models import Entrance

__author__ = 'abolfazl'


class TaskReadyDataEditForm(ModelForm):
    file = forms.FileField(required=True,
                             widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    class Meta:
        model = ReadyData
        fields = ['file', ]