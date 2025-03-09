# tests/forms.py

from django import forms

from .models import SignatureModel


class SignatureModelForm(forms.ModelForm):
    class Meta:
        model = SignatureModel
        fields = ["signature"]
