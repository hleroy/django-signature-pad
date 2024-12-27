# tests/forms.py

from django import forms

from signature_pad.fields import SignaturePadWidget

from .models import SignatureModel


class SignatureModelForm(forms.ModelForm):
    class Meta:
        model = SignatureModel
        fields = ["signature"]


class CustomSignatureModelForm(forms.ModelForm):
    class Meta:
        model = SignatureModel
        fields = ["signature"]
        widgets = {
            "signature": SignaturePadWidget(attrs={"width": 600, "height": 300}),
        }
