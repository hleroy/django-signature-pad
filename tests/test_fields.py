# tests/test_fields.py

from django.test import TestCase

from signature_pad.fields import SignaturePadWidget

from .forms import SignatureModelForm


class SignaturePadTests(TestCase):
    def test_field_widget(self):
        form = SignatureModelForm()
        self.assertIsInstance(form.fields["signature"].widget, SignaturePadWidget)

    def test_widget_default_attrs(self):
        widget = SignaturePadWidget()
        self.assertEqual(widget.attrs["width"], 400)
        self.assertEqual(widget.attrs["height"], 200)

    def test_widget_custom_attrs(self):
        widget = SignaturePadWidget(attrs={"width": 500, "height": 300})
        self.assertEqual(widget.attrs["width"], 500)
        self.assertEqual(widget.attrs["height"], 300)

    def test_widget_media(self):
        widget = SignaturePadWidget()
        self.assertIn("signature_pad/js/signature_pad_widget.js", widget.media._js)
        self.assertIn("signature_pad/css/signature_pad_widget.css", widget.media._css["all"])


#     def test_signature_field_default_widget_attrs(self):
#         """
#         Test that the widget has the correct default attributes.
#         """
#         form = SignatureModelForm()
#         widget = form.fields["signature"].widget
#         self.assertEqual(widget.attrs["width"], 400)
#         self.assertEqual(widget.attrs["height"], 200)

#     def test_signature_field_custom_widget_attrs(self):
#         """
#         Test that custom widget attributes are correctly applied.
#         """
#         form = CustomSignatureModelForm()
#         widget = form.fields["signature"].widget
#         self.assertEqual(widget.attrs["width"], 600)
#         self.assertEqual(widget.attrs["height"], 300)
