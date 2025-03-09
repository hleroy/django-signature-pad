import base64
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Widget
from django.utils.translation import gettext_lazy as _


class SignaturePadWidget(Widget):
    """Widget for capturing handwritten signatures using the signature_pad JavaScript library.

    This widget renders a canvas element that allows users to draw their signature
    with a mouse or touch input. The signature is then converted to a PNG data URL
    and stored in a hidden input field.

    Attributes:
        signature_pad_options (dict): Configuration options for the signature pad.
            Supported options include:
            - dotSize: Size of the drawing dot
            - minWidth: Minimum width of the signature line
            - maxWidth: Maximum width of the signature line
            - backgroundColor: Canvas background color
            - penColor: Signature line color

    Security:
        The widget itself doesn't perform validation. Security checks are
        implemented in the associated SignaturePadField class.
    """

    template_name = "signature_pad/widgets/signature_pad.html"

    # Signature pad options with default values
    signature_pad_options = {
        "dotSize": None,
        "minWidth": None,
        "maxWidth": None,
        "backgroundColor": None,
        "penColor": None,
    }

    def __init__(self, attrs=None, **kwargs):
        """Initialize the widget with optional configuration.

        Args:
            attrs (dict, optional): HTML attributes for the rendered widget.
            **kwargs: Additional options for the signature pad, such as dotSize,
                minWidth, maxWidth, backgroundColor, or penColor.
        """
        self.signature_pad_options = self.signature_pad_options.copy()

        # Extract signature pad options from kwargs
        for option_name in self.signature_pad_options.keys():
            if option_name in kwargs:
                self.signature_pad_options[option_name] = kwargs.pop(option_name)

        super().__init__(attrs, **kwargs)

    def get_context(self, name, value, attrs):
        """Get the rendering context for the widget.

        Args:
            name (str): The name of the field.
            value (str): The value of the field.
            attrs (dict): HTML attributes for the rendered widget.

        Returns:
            dict: Context for rendering the widget template.
        """
        context = super().get_context(name, value, attrs)
        context["widget"]["signature_pad_options"] = {
            k: v for k, v in self.signature_pad_options.items() if v is not None
        }
        return context

    class Media:
        js = ("signature_pad/js/signature_pad_widget.js",)
        css = {"all": ("signature_pad/css/signature_pad_widget.css",)}


class SignaturePadField(models.TextField):
    """Django model field for storing handwritten signatures as PNG data URLs.

    This field stores signatures as base64-encoded PNG data URLs and provides
    comprehensive security validation to prevent malicious input.

    Attributes:
        max_size_kb (int): Maximum allowed size for the signature in kilobytes.
            Defaults to 100KB.

    Security Controls:
        1. Format Validation: Ensures the data follows the exact format
           'data:image/png;base64,' followed by valid base64 characters.
        2. Base64 Decoding Verification: Validates that the base64 data
           is correctly formatted and can be decoded.
        3. PNG Header Verification: Confirms the decoded data begins with
           the standard PNG file signature (89 50 4E 47 0D 0A 1A 0A in hex).
        4. Size Limitation: Enforces a maximum size limit (default: 100KB)
           to prevent denial of service attacks through excessive data.

    Raises:
        ValidationError: When any of the security validation checks fail.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the field with optional configuration.

        Args:
            max_size_kb (int, optional): Maximum allowed size for the signature
                in kilobytes. Defaults to 100KB.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.max_size_kb = kwargs.pop("max_size_kb", 100)  # Default max size: 100KB
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """Return a form field appropriate for this model field.

        Args:
            **kwargs: Additional arguments to pass to the form field.

        Returns:
            django.forms.Field: A form field instance configured with
                SignaturePadWidget as the widget.
        """
        kwargs["widget"] = SignaturePadWidget()
        return super().formfield(**kwargs)

    def validate_png_data_url(self, value):
        """Validate that the value is a properly formatted PNG data URL.

        Performs multiple security checks to ensure the data is safe:
        1. Verifies the correct data URL format for PNG
        2. Validates the base64 encoding is properly formatted
        3. Confirms the presence of the PNG file signature
        4. Enforces size limitations

        Args:
            value (str): The PNG data URL to validate.

        Raises:
            ValidationError: If any validation check fails, with a specific
                error message describing the issue.
        """
        if not value:
            return

        # Check for correct data URL format for PNG
        if not re.match(r"^data:image/png;base64,[A-Za-z0-9+/]+=*$", value):
            raise ValidationError(_("Invalid PNG data URL format."))

        try:
            # Extract the base64 data part
            header, base64_data = value.split(",", 1)

            # Validate it's proper base64
            decoded_data = base64.b64decode(base64_data)

            # Check for PNG signature in the decoded data
            if not decoded_data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValidationError(_("Invalid PNG data: missing PNG signature."))

            # Check size
            kb_size = len(decoded_data) / 1024
            if kb_size > self.max_size_kb:
                raise ValidationError(
                    _("Signature image is too large (%(size).2f KB). Maximum allowed size is %(max_size)d KB."),
                    params={"size": kb_size, "max_size": self.max_size_kb},
                )

        except (ValueError, base64.binascii.Error):
            raise ValidationError(_("Invalid base64 data in the PNG data URL."))

    def clean(self, value, model_instance):
        """Validate the signature data before saving to the database.

        Args:
            value (str): The PNG data URL to validate.
            model_instance: The model instance the field belongs to.

        Returns:
            str: The validated value.

        Raises:
            ValidationError: If any validation check fails.
        """
        value = super().clean(value, model_instance)
        self.validate_png_data_url(value)
        return value
