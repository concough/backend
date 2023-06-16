# coding=utf-8
from django import forms
from django.forms import Form

from admin.Forms.FormHelpers import error_messages


class ReportExternalCampaignAddForm(Form):
    title = forms.CharField(max_length=500, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['title', ]