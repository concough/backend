# coding=utf-8
from django.forms import ModelForm
from django import forms

from api.models import AppVersionRepo
from main.Forms.FormHelpers import error_messages


class AppVersionRepoAddForm(ModelForm):
    device = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "دستگاه", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    version = forms.IntegerField(required=True,
                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                           'placeholder': "ورژن"}),
                             error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = AppVersionRepo
        fields = ['device', 'version']