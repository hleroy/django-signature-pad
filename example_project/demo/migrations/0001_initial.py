# Generated by Django 5.1.7 on 2025-03-09 14:38

import signature_pad.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("signature", signature_pad.fields.SignaturePadField(blank=True, null=True)),
            ],
        ),
    ]
