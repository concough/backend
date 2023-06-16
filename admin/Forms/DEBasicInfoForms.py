# coding=utf-8
from django import forms
from django.forms.models import ModelForm
from admin.Forms.FormHelpers import error_messages, YEAR_CHOICES, MONTH_CHOICES
from dataentry.models import TaskMessageType
from main.Helpers.model_static_values import ENTRANCE_SALE_COST_TYPES, ENTRANCE_TAG_SALE_Q_COUNT
from main.models import Organization, EntranceType, ExaminationGroup, EntranceSet, EntranceLesson, EntranceSubset, \
    EntranceSaleData, EntranceTagSaleData

__author__ = 'abolfazl'


class OrganizationAddForm(ModelForm):
    title = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    image = forms.ImageField(required=False, allow_empty_file=False,
                             widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = Organization
        fields = ['title', 'image']


class EntranceTypeAddForm(ModelForm):
    title = forms.CharField(max_length=200, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    code = forms.CharField(max_length=10, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "کد"}),
                            error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceType
        fields = ['title', 'code',]


class ExaminationGroupAddForm(ModelForm):
    title = forms.CharField(max_length=200, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    etype = forms.ModelChoiceField(queryset=EntranceType.objects.all(), required=True, empty_label=None,
                                   widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = ExaminationGroup
        fields = ['title', 'etype']


class EntranceSetAddForm(ModelForm):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    group = forms.ModelChoiceField(queryset=ExaminationGroup.objects.all().prefetch_related('etype'), required=True, empty_label=None,
                                   widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)
    code = forms.IntegerField(min_value=0, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)

    image = forms.ImageField(required=False, allow_empty_file=False,
                                            widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceSet
        fields = ['title', 'group', 'image', 'code']


class EntranceSetEditForm(ModelForm):
    image = forms.ImageField(required=False, allow_empty_file=False,
                                            widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)
    code = forms.IntegerField(min_value=0, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceSet
        fields = ['image', 'code']


class EntranceLessonAddForm(ModelForm):
    title = forms.CharField(max_length=200, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    full_title = forms.CharField(max_length=500, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان کامل", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceLesson
        fields = ['title', 'full_title']


class EntranceSubsetAddForm(ModelForm):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    e_set = forms.ModelChoiceField(queryset=EntranceSet.objects.all().prefetch_related('group'), required=True,
                                   empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}),
                                   error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceSubset
        fields = ['title', 'e_set']


class TaskMessageTypeAddForm(ModelForm):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = TaskMessageType
        fields = ['title', ]


