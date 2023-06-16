# coding=utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.forms import Form
from django.forms.utils import ErrorList
from main.Forms.FormHelpers import error_messages

__author__ = 'abolfazl'


class LoginForm(Form):
    username = forms.CharField(max_length=256, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control input-lg', 'placeholder': 'Username'}), error_messages=error_messages)
    password = forms.CharField(max_length=256, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}), error_messages=error_messages)
    keep_me_logged_in = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox'}))

    class Meta:
        fields = ['username', 'password', 'keep_me_logged_in']


class _HomeAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(_HomeAuthenticationForm, self).__init__(request, *args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Username'})
        self.fields['username'].error_messages = error_messages

        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password'].error_messages = error_messages


class _AuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(_AuthenticationForm, self).__init__(request, *args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Username'})
        self.fields['username'].error_messages = error_messages

        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Password'})
        self.fields['password'].error_messages = error_messages


class _PasswordChangeForm(PasswordChangeForm):

    error_messages = dict(PasswordChangeForm.error_messages, **error_messages)

    def __init__(self, user, *args, **kwargs):
        super(_PasswordChangeForm, self).__init__(user, *args, **kwargs)

        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'گذر واژه قدیمی'})
        self.fields['old_password'].error_messages = error_messages

        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'گذر واژه جدید'})
        self.fields['new_password1'].error_messages = error_messages

        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تکرار گذر واژه جدید'})
        self.fields['new_password2'].error_messages = error_messages


class _PasswordResetForm(PasswordResetForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False):
        super(_PasswordResetForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                 empty_permitted)

        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email Address'})
        self.fields['email'].error_messages = error_messages


class _SetPasswordForm(SetPasswordForm):
    error_messages = dict(SetPasswordForm.error_messages, **error_messages)

    def __init__(self, user, *args, **kwargs):
        super(_SetPasswordForm, self).__init__(user, *args, **kwargs)

        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'گذر واژه جدید'})
        self.fields['new_password1'].error_messages = error_messages

        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تکرار گذر واژه جدید'})
        self.fields['new_password2'].error_messages = error_messages


class _PasswordResetForm2(Form):
    username = forms.CharField(max_length=256, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': 'Username'}), error_messages=error_messages)

    class Meta:
        fields = ['username',]


class _SetPasswordForm2(Form):
    error_messages = dict(SetPasswordForm.error_messages, **error_messages)
    user = None

    token = forms.CharField(max_length=256, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg text-center', 'placeholder': '_ _ _ _ _ _'}), error_messages=error_messages)
    new_password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'New Password'}), error_messages=error_messages)
    new_password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm ٔNew Password'}),
                                        error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(_SetPasswordForm2, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        # password_validation.validate_password(password2, self.user)
        return password2

    def save(self, user, commit=True):
        password = self.cleaned_data["new_password1"]
        user.set_password(password)
        if commit:
            user.save()
        return user

    class Meta:
        fields = ['token', "new_password1", "new_password2"]
