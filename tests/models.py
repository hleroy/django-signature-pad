# tests/models.py

from django.db import models

from signature_pad.fields import SignaturePadField


class SignatureModel(models.Model):
    signature = SignaturePadField()

    class Meta:
        app_label = "tests"
