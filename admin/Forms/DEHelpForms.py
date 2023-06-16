# coding=utf-8
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms.forms import Form

from admin.Forms.FormHelpers import error_messages

HELP_LANGUAGE = (
    ("fa", u"فارسی"),
    ("en", u"English"),
)


HELP_DEVICES = (
    ("android", u"Android"),
    ("ios", u"iOS"),
    ("desktop", u"Desktop"),
)


class HelpSectionsForm(Form):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    color = forms.CharField(max_length=10, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'color',
                                                          'placeholder': "رنگ"}),
                            error_messages=error_messages)
    image = forms.FileField(required=False, allow_empty_file=False,
                           widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['title', 'color', 'image']


class HelpSectionLangAddForm(Form):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    lang = forms.ChoiceField(choices=HELP_LANGUAGE, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['title', 'lang']


class HelpSectionSubAddForm(Form):
    title = forms.CharField(max_length=500, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    order = forms.IntegerField(min_value=1, required=True,
                            widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'placeholder': "ردیف"}), error_messages=error_messages)
    description = forms.CharField(required=True, widget=CKEditorUploadingWidget(attrs={'class': 'form-control',
                                                          'placeholder': "توضیحات"}), error_messages=error_messages)


    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['title', 'order', 'description']


class HelpSectionSubEditForm(Form):
    order = forms.IntegerField(min_value=1, required=True,
                            widget=forms.NumberInput(attrs={'class': 'form-control',
                                                          'placeholder': "ردیف"}), error_messages=error_messages)
    description = forms.CharField(required=True, widget=CKEditorUploadingWidget(attrs={'class': 'form-control',
                                                          'placeholder': "توضیحات"}), error_messages=error_messages)


    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['order', 'description']


class HelpSectionSubDeviceAddForm(Form):
    device = forms.ChoiceField(choices=HELP_DEVICES, required=True,
                             widget=forms.Select(attrs={'class': 'form-control'}),
                             error_messages=error_messages)
    description = forms.CharField(required=True, widget=CKEditorUploadingWidget(attrs={'class': 'form-control',
                                                          'placeholder': "توضیحات"}), error_messages=error_messages)


    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['device', 'description']


class HelpSectionSubDeviceEditForm(Form):
    description = forms.CharField(required=True, widget=CKEditorUploadingWidget(attrs={'class': 'form-control',
                                                          'placeholder': "توضیحات"}), error_messages=error_messages)


    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['description',]
