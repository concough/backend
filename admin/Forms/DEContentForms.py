# coding=utf-8
from django.forms import ModelForm
from django import forms

from admin.Forms.FormHelpers import error_messages
from main.models import ContentQuotesCategory, ContentQuote

COMPANY_NAME = (
    ("zhycan", u"ژیکان"),
)


class ContentQuotesCategoryAddForm(ModelForm):
    title = forms.CharField(max_length=255, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "عنوان", 'autofocus': 'autofocus'}),
                            error_messages=error_messages)
    code = forms.CharField(max_length=255, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': "کد اختصاصی"}),
                           error_messages=error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = ContentQuotesCategory
        fields = ['title', 'code', ]


class ContentQuotesAddForm(ModelForm):
    title_fa = forms.CharField(required=True,
                            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                          'placeholder': "جمله فارسی"}),
                            error_messages=error_messages)
    title_en = forms.CharField(required=True,
                               widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                            'placeholder': "جمله انگلیسی"}),
                               error_messages=error_messages)
    company_name = forms.ChoiceField(choices=COMPANY_NAME, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  error_messages=error_messages)
    title_back_color = forms.CharField(max_length=10, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'color',
                                                          'placeholder': "رنگ پس زمینه"}),
                                       error_messages=error_messages)

    title_back_alpha = forms.FloatField(min_value=0.0, max_value=1.0, required=True,
                                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1,
                                                                        'value': 0.0, 'type': 'range',
                                                                        'placeholder': "شفافیت پس زمینه"}),
                                        error_messages=error_messages)
    author = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "نویسنده"}),
                            error_messages=error_messages)

    main_image = forms.FileField(required=True, allow_empty_file=False,
                           widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    main_image_back = forms.FileField(required=True, allow_empty_file=False,
                                 widget=forms.FileInput(attrs={'class': 'form-control'}), error_messages=error_messages)

    temp_category = forms.ModelMultipleChoiceField(queryset=ContentQuotesCategory.objects.all(), required=False,
                                              widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
                                                error_messages = error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = ContentQuote
        fields = ['title_fa', 'title_en', 'title_back_alpha', 'title_back_color', 'company_name',
                  'author', 'main_image', 'main_image_back', 'temp_category']


class ContentQuotesEditForm(ModelForm):
    title_fa = forms.CharField(required=True,
                            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                          'placeholder': "جمله فارسی"}),
                            error_messages=error_messages)
    title_en = forms.CharField(required=True,
                               widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                            'placeholder': "جمله انگلیسی"}),
                               error_messages=error_messages)
    title_back_color = forms.CharField(max_length=10, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'color',
                                                          'placeholder': "رنگ پس زمینه"}),
                                       error_messages=error_messages)

    title_back_alpha = forms.FloatField(min_value=0.0, max_value=1.0, required=True,
                                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1,
                                                                        'value': 0.0, 'type': 'range',
                                                                        'placeholder': "شفافیت پس زمینه"}),
                                        error_messages=error_messages)
    author = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "نویسنده"}),
                            error_messages=error_messages)

    temp_category = forms.ModelMultipleChoiceField(queryset=ContentQuotesCategory.objects.all(), required=False,
                                              widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
                                                error_messages = error_messages)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = ContentQuote
        fields = ['title_fa', 'title_en', 'title_back_alpha', 'title_back_color',
                  'author', 'temp_category']
