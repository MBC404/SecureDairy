from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import LetterVersion # cite: uploaded:forms.py


class SignupForm(UserCreationForm):
    class Meta:
        model = User # cite: uploaded:forms.py
        fields = ["username", "password1", "password2"] # cite: uploaded:forms.py


class LetterForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6, 
            'class': 'form-control',
            # CRITICAL FIX: Enforce min-height to fix visibility issue on dark theme
            'style': 'min-height: 150px;' 
        }), 
        label="Letter Content" # cite: uploaded:forms.py
    )


class ModificationForm(forms.Form):
    proposed_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}), # cite: uploaded:forms.py
        label="Proposed Modification" # cite: uploaded:forms.py
    )