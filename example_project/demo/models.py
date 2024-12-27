from django.db import models

from signature_pad import SignaturePadField


class Document(models.Model):
    name = models.CharField(max_length=200)
    signature = SignaturePadField(blank=True, null=True)

    def __str__(self):
        return self.name
