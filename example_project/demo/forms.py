from django import forms

from signature_pad import SignaturePadWidget

from .models import Document


class DocumentForm(forms.ModelForm):
    # Override the field completely instead of just the widget
    signature = forms.CharField(
        widget=SignaturePadWidget(
            dotSize=2.5, penColor="rgb(66, 133, 244)", minWidth=3, maxWidth=7, backgroundColor="rgb(152, 255, 255)"
        )
    )

    class Meta:
        model = Document
        fields = ["name", "signature"]
