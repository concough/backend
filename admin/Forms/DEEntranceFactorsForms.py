from django import forms
from django.forms.models import ModelForm
from admin.Forms.FormHelpers import error_messages
from main.models import EntranceLesson, EntranceSubsetFactor, EntranceSubset

__author__ = 'abolfazl'


class EntranceFactorAddForm(ModelForm):
    factor = forms.IntegerField(min_value=1, max_value=4, widget=forms.NumberInput(attrs={'class': 'form-control'}))


    def __init__(self, ebd_id, eset, *args, **kwargs):
        super(EntranceFactorAddForm, self).__init__(*args, **kwargs)
        self.fields['lesson'] = forms.ModelChoiceField(queryset=EntranceLesson.objects.filter(
            entrance_type__entrances__id=ebd_id), required=True, widget=forms.Select(attrs={'class': 'form-control'}),
                                                       error_messages=error_messages, empty_label=None)
        self.fields['subset'] = forms.ModelChoiceField(queryset=EntranceSubset.objects.filter(e_set=eset),
                                                       required=True, widget=forms.Select(attrs={'class': 'form-control'}),
                                                       error_messages=error_messages, empty_label=None)

    def clean(self):
        for x, y in self.cleaned_data.iteritems():
            if isinstance(y, basestring):
                self.cleaned_data[x] = self.cleaned_data[x].strip()

    class Meta:
        model = EntranceSubsetFactor
        fields = ['factor', 'lesson', 'subset']