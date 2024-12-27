from django.db import models
from django.forms import Widget


class SignaturePadWidget(Widget):
    template_name = "signature_pad/widgets/signature_pad.html"

    def __init__(self, attrs=None):
        default_attrs = {"width": 400, "height": 200}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        js = ("signature_pad/js/signature_pad_widget.js",)
        css = {"all": ("signature_pad/css/signature_pad_widget.css",)}

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value in [None, "null"]:
            value = ""
        context["widget"]["value"] = value
        return context


class SignaturePadField(models.JSONField):
    def formfield(self, **kwargs):
        kwargs["widget"] = SignaturePadWidget()
        return super().formfield(**kwargs)
