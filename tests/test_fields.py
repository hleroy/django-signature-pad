# tests/test_fields.py

import base64

from django.core.exceptions import ValidationError
from django.test import TestCase

from signature_pad.fields import SignaturePadField, SignaturePadWidget, validate_png_data_url

from .forms import SignatureModelForm, SignaturePlainForm
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


class ValidatePNGDataURLTests(TestCase):
    """Tests for the standalone validate_png_data_url validator."""

    def setUp(self):
        # Valid minimal PNG (1x1 transparent pixel) as base64
        self.valid_png_data = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJdijKHqwAAAABJRU5ErkJggg=="
        )
        self.valid_data_url = f"data:image/png;base64,{self.valid_png_data}"

    def test_empty_value_is_allowed(self):
        """Empty values pass validation (required-ness is enforced elsewhere)."""
        validate_png_data_url("")
        validate_png_data_url(None)

    def test_valid_png_data_url(self):
        """A correctly formatted PNG data URL passes without error."""
        validate_png_data_url(self.valid_data_url)

    def test_invalid_data_url_format(self):
        """Incorrectly formatted data URLs are rejected."""
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
            with self.subTest(value=invalid_format):
                with self.assertRaises(ValidationError):
                    validate_png_data_url(invalid_format)

    def test_non_png_data_rejected(self):
        """Data with a valid base64 encoding but no PNG signature is rejected."""
        text_base64 = base64.b64encode(b"This is not a PNG file").decode("ascii")
        fake_png_url = f"data:image/png;base64,{text_base64}"

        with self.assertRaises(ValidationError):
            validate_png_data_url(fake_png_url)

    def test_trailing_newline_rejected(self):
        """Trailing newline is rejected (\\Z anchor, not $ which allows a trailing \\n)."""
        with self.assertRaises(ValidationError):
            validate_png_data_url(self.valid_data_url + "\n")

    def test_excessive_base64_padding_rejected(self):
        """More than two padding characters (===) are rejected by the regex."""
        stripped = self.valid_png_data.rstrip("=")
        with self.assertRaises(ValidationError):
            validate_png_data_url(f"data:image/png;base64,{stripped}===")

    def test_strict_base64_decode_rejects_bad_padding(self):
        """base64.b64decode(validate=True) rejects data with incorrect padding length."""
        # 15-char base64 string — length is not a multiple of 4, so padding is wrong.
        # The regex allows zero padding chars, but strict decode requires a valid length.
        unpadded = "SGVsbG8gV29ybGQ"  # "Hello World" without the trailing =
        with self.assertRaises(ValidationError):
            validate_png_data_url(f"data:image/png;base64,{unpadded}")

    def test_standalone_callable(self):
        """validate_png_data_url is importable and callable without a field instance."""
        from signature_pad import validate_png_data_url as imported_validator

        # Should raise for invalid input
        with self.assertRaises(ValidationError):
            imported_validator("not-a-png")

        # Should pass for valid input
        imported_validator(self.valid_data_url)


class SignaturePadFieldSecurityTests(TestCase):
    def setUp(self):
        self.valid_png_data = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJdijKHqwAAAABJRU5ErkJggg=="
        )
        self.valid_data_url = f"data:image/png;base64,{self.valid_png_data}"
        self.field = SignaturePadField(max_size_kb=100)
        self.model_instance = SignatureModel()

    def test_custom_max_size(self):
        """Field initialises with the given max_size_kb; default is 100."""
        custom_field = SignaturePadField(max_size_kb=200)
        self.assertEqual(custom_field.max_size_kb, 200)

        default_field = SignaturePadField()
        self.assertEqual(default_field.max_size_kb, 100)

    def test_size_limit_enforced_via_clean(self):
        """clean() raises ValidationError when the decoded image exceeds max_size_kb."""
        small_field = SignaturePadField(max_size_kb=0.01)  # ~10 bytes — tiny limit

        with self.assertRaises(ValidationError) as cm:
            small_field.clean(self.valid_data_url, self.model_instance)

        self.assertIn("too large", str(cm.exception))

    def test_clean_validates_format(self):
        """clean() propagates format errors from validate_png_data_url."""
        with self.assertRaises(ValidationError):
            self.field.clean("data:image/png;base64,notvalidbase64!!!", self.model_instance)

    def test_formfield_has_png_validators(self):
        """formfield() attaches validate_png_data_url to the returned form field."""
        form_field = self.field.formfield()
        self.assertIn(validate_png_data_url, form_field.validators)

    def test_formfield_has_size_validator(self):
        """formfield() attaches the size validator to the returned form field."""
        form_field = self.field.formfield()
        validator_names = [getattr(v, "__name__", None) or type(v).__name__ for v in form_field.validators]
        self.assertIn("_validate_size", validator_names)

    def test_modelform_validation(self):
        """Validation works through ModelForm processing."""
        form = SignatureModelForm(data={"signature": self.valid_data_url})
        self.assertTrue(form.is_valid())

        form = SignatureModelForm(data={"signature": "data:image/png;base64,invalid"})
        self.assertFalse(form.is_valid())
        self.assertIn("signature", form.errors)

    def test_plain_form_validation(self):
        """Validation fires at the form layer even without a ModelForm.

        This exercises the validators added in formfield() and ensures the HIGH
        gap (no form-level validation for plain Forms) is closed.
        """
        form = SignaturePlainForm(data={"signature": self.valid_data_url})
        self.assertTrue(form.is_valid())

        form = SignaturePlainForm(data={"signature": "data:image/png;base64,bm90YXBuZw=="})
        self.assertFalse(form.is_valid())
        self.assertIn("signature", form.errors)

    def test_form_with_no_comma_value_does_not_crash(self):
        """A submitted value without a comma must not raise IndexError.

        Django's run_validators collects ValidationError and keeps going, so
        the size validator runs even after the format validator rejects the
        input. Splitting on ',' would otherwise raise IndexError and bubble
        up as a 500.
        """
        form = SignaturePlainForm(data={"signature": "no-comma-here"})
        self.assertFalse(form.is_valid())
        self.assertIn("signature", form.errors)

    def test_plain_form_size_limit(self):
        """Size validator on the form field rejects oversized data via plain Form."""

        class TinyForm(SignaturePlainForm):
            signature = SignaturePadField(max_size_kb=0.01).formfield()

        form = TinyForm(data={"signature": self.valid_data_url})
        self.assertFalse(form.is_valid())
        self.assertIn("signature", form.errors)
        self.assertTrue(any("too large" in e for e in form.errors["signature"]))
