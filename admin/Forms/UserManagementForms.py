# coding=utf-8
from django import forms
from django.contrib.auth.models import User, Group
from django.forms.utils import ErrorList
from admin.Forms.FormHelpers import error_messages
from main.models import UserCheckerState

__author__ = 'abolfazl'


USER_CHECKER_STATE_TYPE = (
    ("SINGLE", u"فقط مرحله اول"),
    ("FULL", u"کامل"),
)


class UserInGroupChoiceField(forms.ModelChoiceField):
    def __init__(self, group_name, *args, **kwargs):
        super(UserInGroupChoiceField, self).__init__(
            queryset=User.objects.filter(groups__name=group_name, is_active=True),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return unicode(obj.get_full_name() + " " + obj.username)


class GroupsChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        #return super(GroupsChoiceField, self).label_from_instance(obj)
        return str(obj.name)

    def __init__(self, queryset, *args, **kwargs):
        super(GroupsChoiceField, self).__init__(queryset=Group.objects.all(),
                                                *args, **kwargs)


class UserAddForm(forms.ModelForm):

    temp_groups = GroupsChoiceField(queryset=(), error_messages=error_messages,
                                    widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None):
        super(UserAddForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                          empty_permitted, instance)

        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['username'].error_messages = error_messages

        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password'].error_messages = error_messages

        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})
        self.fields['email'].error_messages = error_messages

        self.fields['first_name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['first_name'].error_messages = error_messages

        self.fields['last_name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['last_name'].error_messages = error_messages

        self.fields['is_staff'].widget = forms.CheckboxInput(attrs={'class': 'checkbox'})
        self.fields['is_staff'].error_messages = error_messages

        #self.fields['_groups'] = forms.MultipleChoiceField(choices=Group.objects.all())
        #self.fields['_groups'].error_messages = error_messages

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'temp_groups']


class UserEditForm(forms.ModelForm):

    temp_groups = GroupsChoiceField(queryset=(), error_messages=error_messages,
                                    widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None):
        super(UserEditForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                          empty_permitted, instance)

        self.fields['first_name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['first_name'].error_messages = error_messages

        self.fields['last_name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['last_name'].error_messages = error_messages

        self.fields['is_staff'].widget = forms.CheckboxInput(attrs={'class': 'checkbox'})
        self.fields['is_staff'].error_messages = error_messages

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'is_staff', 'temp_groups']


class UserCheckerStateChangeForm(forms.ModelForm):
    user = UserInGroupChoiceField("check_in", required=True, widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)

    state = forms.ChoiceField(choices=USER_CHECKER_STATE_TYPE, required=True,
                                              widget=forms.Select(attrs={'class': 'form-control'}),
                                              error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(UserCheckerStateChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = UserCheckerState
        fields = ['user', 'state']
