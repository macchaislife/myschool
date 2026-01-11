from django import forms
from .models import Opinion, SurveyResponse

class OpinionForm(forms.ModelForm):
    class Meta:
        model = Opinion
        fields = ['category', 'content', 'image']
