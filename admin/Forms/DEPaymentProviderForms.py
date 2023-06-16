# coding=utf-8
from django.forms import ModelForm
from django import forms

from admin.Forms.FormHelpers import error_messages
from main.models import PaymentProvider


class PaymentProviderAddForm(ModelForm):
    name = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "نام", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    mmerchant_id = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "کد"}),
                            error_messages=error_messages)
    email = forms.CharField(max_length=100, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                 'placeholder': "پست الکترونیکی"}),
                                   error_messages=error_messages)
    phone = forms.CharField(max_length=100, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "شماره همراه"}),
                            error_messages=error_messages)
    callback_url = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "آدرس بازگشت"}),
                            error_messages=error_messages)
    webservice_url = forms.CharField(required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                 'placeholder': "آدرس وب سرویس"}),
                                   error_messages=error_messages)
    pay_url = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                                   'placeholder': "آدرس پرداخت"}),
                                     error_messages=error_messages)
    logo = forms.ImageField(required=False, allow_empty_file=False,
                         widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = PaymentProvider
        fields = ['name', 'mmerchant_id', 'email', 'phone', 'callback_url', 'webservice_url', 'pay_url', 'logo']
