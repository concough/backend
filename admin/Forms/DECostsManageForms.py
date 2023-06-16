# coding=utf-8
from django import forms
from django.forms.models import ModelForm

from admin.Forms.FormHelpers import error_messages, YEAR_CHOICES, MONTH_CHOICES
from main.Helpers.model_static_values import ENTRANCE_TAG_SALE_Q_COUNT, CONCOUGH_GIFT_CARD_TYPES
from main.models import EntranceType, EntranceSaleData, EntranceTagSaleData, ConcoughGiftCard


class EntranceSaleDataAddForm(ModelForm):
    entrance_type = forms.ModelChoiceField(queryset=EntranceType.objects.all(), required=True,
                                   empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}),
                                   error_messages=error_messages)

    cost = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "قیمت"}))
    cost_bon = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "بن"}))
    year = forms.ChoiceField(required=True, choices=YEAR_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))
    month = forms.ChoiceField(required=True, choices=MONTH_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceSaleData
        fields = ['entrance_type', 'cost', 'cost_bon', 'year', 'month']


class EntranceTagsSaleDataAddForm(ModelForm):
    entrance_type = forms.ModelChoiceField(queryset=EntranceType.objects.all(), required=True,
                                   empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}),
                                   error_messages=error_messages)

    cost = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "قیمت برای %d سوال" % ENTRANCE_TAG_SALE_Q_COUNT}))
    year = forms.ChoiceField(required=True, choices=YEAR_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))
    month = forms.ChoiceField(required=True, choices=MONTH_CHOICES, widget=forms.Select(attrs={"class": 'form-control'}))

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceTagSaleData
        fields = ['entrance_type', 'cost', 'year', 'month']


class ConcoughGiftCardAddForm(ModelForm):
    cost = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "قیمت"}))
    description = forms.CharField(required=True, max_length=300,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': "توضیحات"}),
                               error_messages=error_messages)
    gift_type = forms.ChoiceField(required=True, choices=CONCOUGH_GIFT_CARD_TYPES, widget=forms.Select(attrs={"class": 'form-control'}))
    charge = forms.IntegerField(required=True, min_value=0,
                              widget=forms.NumberInput(attrs={"class": 'form-control', "placeholder": "بنکوق"}))

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = ConcoughGiftCard
        fields = ['description', 'cost', 'charge', 'gift_type']