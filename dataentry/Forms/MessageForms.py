from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseForm, ModelForm
from admin.Forms.FormHelpers import error_messages
from dataentry.models import TaskMessageType, TaskMessage

__author__ = 'abolfazl'


class MessageReplyForm(ModelForm):
    message_type = forms.ModelChoiceField(queryset=TaskMessageType.objects.all(), required=True,
                                          widget=forms.Select(attrs={'class': 'form-control',
                                                                     'autofocus': 'autofocus'}),
                                          error_messages=error_messages, empty_label=None)

    attached_file = forms.FileField(required=False,
                                    widget=forms.FileInput(attrs={'class': 'form-control'}),
                                    error_messages=error_messages)

    message_content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
                                      error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = TaskMessage
        fields = ['message_type', 'attached_file', 'message_content']


class MessageNewForm(ModelForm):
    message_type = forms.ModelChoiceField(queryset=TaskMessageType.objects.all(), required=True,
                                          widget=forms.Select(attrs={'class': 'form-control',
                                                                     'autofocus': 'autofocus'}),
                                          error_messages=error_messages, empty_label=None)

    attached_file = forms.FileField(required=False,
                                    widget=forms.FileInput(attrs={'class': 'form-control'}),
                                    error_messages=error_messages)

    message_content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
                                      error_messages=error_messages)

    to_user = forms.ModelChoiceField(queryset=User.objects.filter(groups__name__in=['editor', 'picture_creator']),
                                     required=True,
                                     widget=forms.Select(attrs={'class': 'form-control'}),
                                     error_messages=error_messages, empty_label=None)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = TaskMessage
        fields = ['message_type', 'attached_file', 'message_content', 'to_user']
