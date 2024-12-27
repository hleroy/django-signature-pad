from django import template

from ..utils import signature_to_data_url

register = template.Library()


@register.filter
def signature_base64(value):
    """
    Template filter to convert signature data to base64 image URL.

    Usage:
        {% load signature_filters %}
        <img src="{{ obj.signature|signature_base64 }}" alt="Signature" />
    """
    if not value or not isinstance(value, list):
        return ""

    return signature_to_data_url(value)
