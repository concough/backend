# coding=utf-8
from django import forms
from django.forms import Form
from django.forms.models import ModelForm

from admin.Forms.FormHelpers import error_messages

__author__ = 'abolfazl'


class SearchForm(Form):
    q = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "جستجو", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['q', ]