# tests/forms.py

from django import forms

from signature_pad.fields import SignaturePadField

from .models import SignatureModel


class SignatureModelForm(forms.ModelForm):
    class Meta:
        model = SignatureModel
        fields = ["signature"]


class SignaturePlainForm(forms.Form):
    """Plain (non-ModelForm) form used to verify form-level PNG validation."""

    signature = SignaturePadField().formfield()
