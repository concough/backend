# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms import Form, ModelForm

from admin.Forms.FormHelpers import error_messages
from main.models import UserCheckerEntranceCost


class UserInGroupChoiceField(forms.ModelChoiceField):
    def __init__(self, group_name, *args, **kwargs):
        super(UserInGroupChoiceField, self).__init__(
            queryset=User.objects.filter(groups__name=group_name, is_active=True),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return unicode(obj.get_full_name() + " " + obj.username)


TYPE_FILE_CONTENT = (
    ("NORMAL", u"عادی"),
    ("PROFESSIONAL", u"تخصصی"),
    ("HALF-PROFESSIONAL", u"نیمه تخصصی"),
)


class JobTaskAddTypistForm(Form):
    job_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    task_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    price_per_q = forms.IntegerField(min_value=100, max_value=1000, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    orig_file = forms.FileField(required=True, allow_empty_file=False,
                           widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)
    file_type = forms.ChoiceField(choices=TYPE_FILE_CONTENT, required=True,
                                              widget=forms.RadioSelect(attrs={'class': 'radio-inline'}),
                                              error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskAddTypistForm, self).__init__(*args, **kwargs)
        self.fields['typist'] = UserInGroupChoiceField("editor", widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['typist', 'price_per_q', 'orig_file', 'job_unique_key', 'task_unique_key', 'file_type']


class JobTaskUploadTermForm(Form):
    job_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    task_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    term_file = forms.FileField(required=True, allow_empty_file=False,
                                widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskUploadTermForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['term_file', 'job_unique_key', 'task_unique_key']


class JobTaskCheckDoneForm(Form):
    job_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    task_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    term_file = forms.FileField(required=True, allow_empty_file=False,
                                widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)
    misspelling_count = forms.IntegerField(min_value=0, max_value=15, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 80}),
                                  error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskCheckDoneForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['term_file', 'job_unique_key', 'task_unique_key', 'misspelling_count', 'description']


class JobTaskFinalPriceForm(Form):
    job_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    task_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    final_cost = forms.IntegerField(min_value=100, max_value=1000, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskFinalPriceForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['job_unique_key', 'task_unique_key', 'final_cost']


RejectReasonChoices = (
    ("SPELLING_MISTAKE", u"غلط املایی زیاد"),
    ("INAPPROPRIATE_EDIT", u"ویرایش نامناسب"),
    ("SHAPE_BUGS", u"اشکال در شکل ها"),
    ("FORMULA_BUGS", u"اشکال در فرمول ها"),
    ("WRONG_FILE", u"عدم تطابق فایل تایپ شده"),
)


class JobTaskEntranceRejectForm(Form):
    job_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    task_unique_key = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    description = forms.CharField(required=False,
                                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 80}),
                                           error_messages=error_messages)
    reject_reason = forms.MultipleChoiceField(choices=RejectReasonChoices, required=True,
                                   widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}), error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskEntranceRejectForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['job_unique_key', 'task_unique_key', 'description', 'reject_reason']


class JobTaskEntrancePayOffForm(Form):
    user_id = forms.IntegerField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    deposit_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                           error_messages=error_messages)
    issue_tracking = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(JobTaskEntrancePayOffForm, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['user_id', 'deposit_id', 'issue_tracking']


class UserCheckerEntranceCostAddForm(ModelForm):
    title = forms.ChoiceField(choices=TYPE_FILE_CONTENT, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)
    rate = forms.FloatField(required=True, min_value=1.0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "نرخ"}))
    cost = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "قیمت"}))

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = UserCheckerEntranceCost
        fields = ['title', 'cost', 'rate']
