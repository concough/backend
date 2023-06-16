# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms import Form
from django.forms.models import ModelForm
from admin.Forms.FormHelpers import error_messages, YEAR_CHOICES, MONTH_CHOICES
from main.models import Organization, Entrance, EntranceType, EntranceSet, EntranceBooklet, EntranceBookletDetail, \
    EntranceLesson, EntranceQuestion, EntranceQuestionImages, EntranceMulti

__author__ = 'abolfazl'


class UserInGroupChoiceField(forms.ModelChoiceField):
    def __init__(self, group_name, *args, **kwargs):
        super(UserInGroupChoiceField, self).__init__(
            queryset=User.objects.filter(groups__name=group_name, is_active=True),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return unicode(obj.get_full_name() + " " + obj.username)


class EntranceLessonChoiceField(forms.ChoiceField):
    def __init__(self, ebd_id, *args, **kwargs):
        try:
            query = EntranceBookletDetail.objects.get(pk=ebd_id)
            q_from = query.q_from
            q_to = query.q_to
            super(EntranceLessonChoiceField, self).__init__(choices=[(x, x) for x in xrange(q_from, q_to + 1)],
                                                            *args, **kwargs)
        except:
            super(EntranceLessonChoiceField, self).__init__(choices=[], *args, **kwargs)


class EntranceQuestionChoiceField(forms.ModelChoiceField):
    def __init__(self, ebd_id, *args, **kwargs):
        super(EntranceQuestionChoiceField, self).__init__(
            queryset=EntranceQuestion.objects.filter(booklet_detail__id=ebd_id).order_by('question_number'),
            empty_label=None, *args, **kwargs)

    def label_from_instance(self, obj):
        return str(obj.question_number)


class EntranceMultiChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, set_id, *args, **kwargs):
        super(EntranceMultiChoiceField, self).__init__(
            queryset=Entrance.objects.filter(entrance_set__id=set_id, published=True), *args, **kwargs)

    def label_from_instance(self, obj):
        return "%s - %s" % (obj.year, obj.month)


class EntranceAddForm(ModelForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=True, empty_label=None,
                                          widget=forms.Select(attrs={'class': 'form-control'}),
                                          error_messages=error_messages)
    entrance_type = forms.ModelChoiceField(queryset=EntranceType.objects.all(), required=True, empty_label=None,
                                           widget=forms.Select(attrs={'class': 'form-control'}),
                                           error_messages=error_messages)
    entrance_set = forms.ModelChoiceField(queryset=EntranceSet.objects.all(), required=True, empty_label=None,
                                          widget=forms.Select(attrs={'class': 'form-control'}),
                                          error_messages=error_messages)
    year = forms.ChoiceField(required=True, choices=YEAR_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))
    month = forms.ChoiceField(required=True, choices=MONTH_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = Entrance
        fields = ['organization', 'entrance_type', 'entrance_set', 'year', 'month']


class EntranceBookletAddForm(ModelForm):
    title = forms.CharField(max_length=300, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    duration = forms.IntegerField(min_value=0, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)

    order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    optional = forms.BooleanField(required=False, widget=forms.CheckboxInput(),
                                  error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceBooklet
        fields = ['title', 'duration', 'order', 'optional', ]


class EntranceBookletDetailAddForm(ModelForm):
    lesson = forms.ModelChoiceField(queryset=EntranceLesson.objects.all(), required=True, empty_label=None,
                                    widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)
    q_from = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                error_messages=error_messages)
    q_to = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages=error_messages)
    order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                               error_messages=error_messages)
    duration = forms.IntegerField(min_value=0, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceBookletDetail
        fields = ['lesson', 'q_from', 'q_to', 'order', 'duration', ]


# answer key choices for flexibility
QuestionAnswerKeyChoices = (
    (0, "No Answer"),
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "1, 2"),
    (6, "1, 3"),
    (7, "1, 4"),
    (8, "2, 3"),
    (9, "2, 4"),
    (10, "3, 4"),
)


class EntranceQuestionEditForm(Form):
    answer_key = forms.ChoiceField(choices=QuestionAnswerKeyChoices, required=True,
                                   widget=forms.Select(attrs={'class': 'form-control'}), error_messages=error_messages)

    def __init__(self, ebd_id, *args, **kwargs):
        super(EntranceQuestionEditForm, self).__init__(*args, **kwargs)
        self.fields['question_number'] = EntranceLessonChoiceField(ebd_id=ebd_id, required=True,
                                                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                                                   error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['answer_key', 'question_number']


class EntranceQuestionEditByFileForm(Form):
    file = forms.FileField(required=False, allow_empty_file=False,
                           widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['file', ]


class EntranceQuestionPictureAddForm(ModelForm):
    image = forms.ImageField(required=True,
                             widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)
    order = forms.IntegerField(min_value=1, initial=1, max_value=10, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                               error_messages=error_messages)

    def __init__(self, ebd_id, *args, **kwargs):
        super(EntranceQuestionPictureAddForm, self).__init__(*args, **kwargs)
        self.fields['question'] = EntranceQuestionChoiceField(ebd_id=ebd_id, required=True,
                                                              widget=forms.Select(attrs={'class': 'form-control'}),
                                                              error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceQuestionImages
        fields = ['image', 'question', 'order']


class EntranceQuestionPictureAddForm2(ModelForm):
    image = forms.ImageField(required=True,
                             widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def __init__(self, *args, **kwargs):
        super(EntranceQuestionPictureAddForm2, self).__init__(*args, **kwargs)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceQuestionImages
        fields = ['image']


class EntranceExtraDataAddForm(Form):
    data_key = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                            'autofocus': 'autofocus'}),
                               error_messages=error_messages)
    data_value = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['data_key', 'data_value', ]


class EntranceJobAssignForm(Form):
    entrance_id = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control'}),
                                     error_messages=error_messages)
    job_supervisor = UserInGroupChoiceField("job_supervisor", widget=forms.Select(attrs={'class': 'form-control',
                                                                                         'autofocus': 'autofocus'}),
                                            error_messages=error_messages)
    orig_file = forms.FileField(required=True, allow_empty_file=False,
                                widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['job_supervisor', 'entrance_id', 'orig_file']


class EntranceMultiAddForm(ModelForm):
    def __init__(self, set_id, *args, **kwargs):
        super(EntranceMultiAddForm, self).__init__(*args, **kwargs)
        self.fields['entrances'] = EntranceMultiChoiceField(set_id=set_id, required=True,
                                                              widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
                                                              error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceMulti
        fields = ['entrances', ]


# 2019-04-23
class EntranceQuestionTagAddForm(Form):
    title = forms.CharField(max_length=255, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'data-action': 'auto-complete',
                                                          'data-ac-url': '/admin/de/tags/',
                                                          'data-ac-area': 'tags-list',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)

    def __init__(self, ebd_id, *args, **kwargs):
        super(EntranceQuestionTagAddForm, self).__init__(*args, **kwargs)
        self.fields['question'] = EntranceQuestionChoiceField(ebd_id=ebd_id, required=True,
                                                              widget=forms.Select(attrs={'class': 'form-control'}),
                                                              error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['title', 'question']


class EntranceQuestionTagFileForm(Form):
    file = forms.FileField(required=False, allow_empty_file=False,
                           widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        fields = ['file', ]
