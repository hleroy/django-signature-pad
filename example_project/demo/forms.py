from django import forms

from signature_pad import SignaturePadWidget

from .models import Document


class DocumentForm(forms.ModelForm):
    # Override the field completely instead of just the widget
    signature = forms.CharField(
        widget=SignaturePadWidget(
            dotSize=1.5, penColor="rgb(0, 0, 0)", minWidth=1, maxWidth=3, backgroundColor="rgb(245, 245, 245)"
        )
    )

    class Meta:
        model = Document
        fields = ["name", "signature"]
