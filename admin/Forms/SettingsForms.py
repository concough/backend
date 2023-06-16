# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm

from admin.Forms.FormHelpers import error_messages
from main.models import UserFinanialInformation


class UserInGroupChoiceField(forms.ModelChoiceField):
    def __init__(self, group_names, *args, **kwargs):
        super(UserInGroupChoiceField, self).__init__(
            queryset=User.objects.filter(groups__name__in=group_names, is_active=True),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return unicode(obj.get_full_name() + " " + obj.username)


class UserFinancialAddForm(ModelForm):
    user = UserInGroupChoiceField(group_names=['master_operator', 'editor', 'check_in'],
                                     required=True,
                                     widget=forms.Select(attrs={'class': 'form-control', 'autofocus': 'autofocus'}),
                                     error_messages=error_messages)

    bank_name = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "نام بانک"}),
                            error_messages=error_messages)
    bank_account_no = forms.CharField(max_length=30, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': "شماره حساب"}),
                                error_messages=error_messages)
    bank_shaba = forms.CharField(max_length=30, required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control',
                                                                    'placeholder': "شماره شبا"}),
                                      error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = UserFinanialInformation
        fields = ['user', 'bank_name', 'bank_account_no', 'bank_shaba']


class UserFinancialEditForm(ModelForm):
    bank_name = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "نام بانک"}),
                            error_messages=error_messages)
    bank_account_no = forms.CharField(max_length=30, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': "شماره حساب"}),
                                error_messages=error_messages)
    bank_shaba = forms.CharField(max_length=30, required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control',
                                                                    'placeholder': "شماره شبا"}),
                                      error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = UserFinanialInformation
        fields = ['bank_name', 'bank_account_no', 'bank_shaba']