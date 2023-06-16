from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from dataentry.models import Task, ReadyData
from main.Forms.FormHelpers import error_messages
from main.models import Entrance

__author__ = 'abolfazl'


class EntranceChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super(EntranceChoiceField, self).__init__(
            queryset=Entrance.objects.filter(assigned_to_task=False).order_by('year', 'month', 'entrance_type').prefetch_related('organization',
                                                                                         'entrance_type',
                                                                                         'entrance_set'),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return "%s - %s: %s (%d/%d)" % (obj.organization.title, obj.entrance_type.title, obj.entrance_set.title,
                                   obj.year, obj.month)


class TaskAddForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.filter(groups__name__in=['master_operator', ])
                                   , required=True, widget=forms.Select(attrs={'class': 'form-control',
                                                                               'autofocus': 'autofocus'}),
                                   error_messages=error_messages, empty_label=None)

    user = forms.ModelChoiceField(queryset=User.objects.filter(groups__name__in=['editor', ])
                                  , required=True, widget=forms.Select(attrs={'class': 'form-control'}),
                                  error_messages=error_messages, empty_label=None)

    entrance = EntranceChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = Task
        fields = ['owner', 'user', 'entrance']


class TaskReadyDataEditForm(ModelForm):
    file = forms.FileField(required=True,
                             widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    class Meta:
        model = ReadyData
        fields = ['file']