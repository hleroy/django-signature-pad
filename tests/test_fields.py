# tests/test_fields.py

import base64

from django.core.exceptions import ValidationError
from django.test import TestCase

from signature_pad.fields import SignaturePadField, SignaturePadWidget

from .forms import SignatureModelForm
from .models import SignatureModel


class SignaturePadWidgetTests(TestCase):
    def test_field_widget(self):
        form = SignatureModelForm()
        self.assertIsInstance(form.fields["signature"].widget, SignaturePadWidget)

    def test_widget_media(self):
        widget = SignaturePadWidget()
        self.assertIn("signature_pad/js/signature_pad_widget.js", widget.media._js)
        self.assertIn("signature_pad/css/signature_pad_widget.css", widget.media._css["all"])

    def test_widget_custom_options(self):
        """Test widget initialization with custom options."""
        widget = SignaturePadWidget(
            dotSize=2.5, minWidth=1.0, maxWidth=4.0, backgroundColor="rgb(255, 255, 255)", penColor="rgb(0, 0, 0)"
        )

        self.assertEqual(widget.signature_pad_options["dotSize"], 2.5)
        self.assertEqual(widget.signature_pad_options["minWidth"], 1.0)
        self.assertEqual(widget.signature_pad_options["maxWidth"], 4.0)
        self.assertEqual(widget.signature_pad_options["backgroundColor"], "rgb(255, 255, 255)")
        self.assertEqual(widget.signature_pad_options["penColor"], "rgb(0, 0, 0)")

    def test_widget_context(self):
        """Test if widget options are correctly included in the context."""
        widget = SignaturePadWidget(penColor="rgb(0, 0, 255)", backgroundColor="rgb(240, 240, 240)")
        context = widget.get_context("signature", None, {})

        # Only non-None options should be included
        self.assertEqual(
            context["widget"]["signature_pad_options"],
            {"penColor": "rgb(0, 0, 255)", "backgroundColor": "rgb(240, 240, 240)"},
        )


class SignaturePadFieldSecurityTests(TestCase):
    def setUp(self):
        """Set up test data for signature validation."""
        # Valid minimal PNG (1x1 transparent pixel) as base64
        self.valid_png_data = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJdijKHqwAAAABJRU5ErkJggg=="
        )
        self.valid_data_url = f"data:image/png;base64,{self.valid_png_data}"

        # Create a field instance for testing
        self.field = SignaturePadField(max_size_kb=100)

        # Mock model instance for clean method tests
        self.model_instance = SignatureModel()

    def test_empty_value_validation(self):
        """Test that empty values pass validation."""
        # Empty string should be valid
        self.field.validate_png_data_url("")

        # None should be valid
        self.field.validate_png_data_url(None)

    def test_valid_png_data_url(self):
        """Test validation of a correctly formatted PNG data URL."""
        # This should not raise an exception
        self.field.validate_png_data_url(self.valid_data_url)

    def test_invalid_data_url_format(self):
        """Test rejection of incorrectly formatted data URLs."""
        invalid_formats = [
            # Wrong mime type
            f"data:image/jpeg;base64,{self.valid_png_data}",
            # Missing base64 indicator
            f"data:image/png,{self.valid_png_data}",
            # No data prefix
            self.valid_png_data,
            # Invalid characters in base64 data
            "data:image/png;base64,$$$$invalid!!!!",
            # Empty data part
            "data:image/png;base64,",
        ]

        for invalid_format in invalid_formats:
            with self.assertRaises(ValidationError):
                self.field.validate_png_data_url(invalid_format)

    def test_invalid_base64_data(self):
        """Test rejection of invalid base64 data."""
        # Data with invalid base64 padding
        invalid_base64 = "data:image/png;base64,SGVsbG8gV29ybGQ="  # "Hello World" without proper padding

        with self.assertRaises(ValidationError):
            self.field.validate_png_data_url(invalid_base64)

    def test_non_png_data(self):
        """Test rejection of data that doesn't have a PNG signature."""
        # Base64 encoded text, not a PNG
        text_base64 = base64.b64encode(b"This is not a PNG file").decode("ascii")
        fake_png_url = f"data:image/png;base64,{text_base64}"

        with self.assertRaises(ValidationError):
            self.field.validate_png_data_url(fake_png_url)

    def test_size_limit(self):
        """Test enforcement of size limits."""
        # Create a field with a very small size limit
        small_field = SignaturePadField(max_size_kb=0.01)  # 10 bytes limit

        # Even our minimal PNG should exceed this tiny limit
        with self.assertRaises(ValidationError) as cm:
            small_field.validate_png_data_url(self.valid_data_url)

        # Verify the error message mentions the size
        self.assertIn("too large", str(cm.exception))

    def test_custom_max_size(self):
        """Test field initialization with custom max_size_kb."""
        custom_field = SignaturePadField(max_size_kb=200)
        self.assertEqual(custom_field.max_size_kb, 200)

        # Default should be 100KB
        default_field = SignaturePadField()
        self.assertEqual(default_field.max_size_kb, 100)

    def test_clean_method_calls_validation(self):
        """Test that the clean method calls validate_png_data_url."""
        # Create a field with a spy on validate_png_data_url
        original_validate = SignaturePadField.validate_png_data_url
        validation_called = False

        def spy_validate(self, value):
            nonlocal validation_called
            validation_called = True
            return original_validate(self, value)

        try:
            # Replace with spy function
            SignaturePadField.validate_png_data_url = spy_validate

            # Call clean
            field = SignaturePadField()
            field.clean(self.valid_data_url, self.model_instance)

            # Verify validation was called
            self.assertTrue(validation_called)

        finally:
            # Restore original function
            SignaturePadField.validate_png_data_url = original_validate

    def test_form_validation(self):
        """Test validation through form processing."""
        # Create a form with valid data
        form = SignatureModelForm(data={"signature": self.valid_data_url})
        self.assertTrue(form.is_valid())

        # Create a form with invalid data
        invalid_data = "data:image/png;base64,invalid"
        form = SignatureModelForm(data={"signature": invalid_data})
        self.assertFalse(form.is_valid())
        self.assertIn("signature", form.errors)
