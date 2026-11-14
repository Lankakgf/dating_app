from django import forms

from .models import Report


class ReportForm(forms.ModelForm):
    also_block = forms.BooleanField(required=False, initial=True, label='Also block this person')

    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {'details': forms.Textarea(attrs={'rows': 4})}