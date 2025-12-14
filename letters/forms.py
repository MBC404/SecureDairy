from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import LetterVersion


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class LetterForm(forms.Form):
    content = forms.CharField(
        # Use a large widget for the message box
        widget=forms.Textarea(attrs={"rows": 6, 'class': 'form-control'}), 
        label="Letter Content"
    )


class ModificationForm(forms.Form):
    proposed_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}),
        label="Proposed Modification"
    )