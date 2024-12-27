# Django Signature Pad

A Django field for capturing signatures using [signature_pad](https://github.com/szimek/signature_pad).

![django_signature_pad.png](django_signature_pad.png)

⚠️ **Important Note**: This package does not include the `signature_pad` JavaScript library. You need to install it separately following the instructions on [GitHub](https://github.com/szimek/signature_pad/).

📦 Common installation methods include:

- Using npm: `npm install signature_pad`
- Using a CDN: `<script src="https://cdn.jsdelivr.net/npm/signature_pad@5.0.4/dist/signature_pad.umd.min.js"></script>`
- Downloading directly from [GitHub releases](https://github.com/szimek/signature_pad/releases)

## Installation

```bash
pip install django-signature-pad
```

## Quick Start

1. Add "signature_pad" to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'signature_pad',
]
```

2. Use the field in your models:

```python
from django.db import models
from signature_pad import SignaturePadField

class Document(models.Model):
    signature = SignaturePadField(blank=True, null=True)
```

3. Customize the widget size (optional, default to 400x200):

```python
from django import forms
from signature_pad import SignaturePadWidget

class MyForm(forms.Form):
    signature = forms.JSONField(
        widget=SignaturePadWidget(attrs={'width': 600, 'height': 300})
    )
```

4. Use it in your form template:

```html
{{ form.media }}
<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <button type="submit">Save</button>
</form>
```

5. Render signature as base64-encoded SVG image URL in your template:

The package includes a template filter for convenient signature rendering in templates:

```html
{% load signature_filters %}

<img src="{{ obj.signature|signature_base64 }}" alt="Signature" />
```

Note: the SVG rendering is not as smooth as `signature_pad` rendering. If you want the same rendering,
render the signature data with `signature_pad`:

```html
{% if obj.signature %}
<canvas id="signature-{{ obj.id }}" width="400" height="200"></canvas>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('signature-{{ obj.id }}');
    const signaturePad = new SignaturePad(canvas);
    signaturePad.fromData({{ obj.signature|safe }});
    signaturePad.off(); // Disable drawing
  });
</script>
{% endif %}
```

## Example Project

Want to see it in action? Try the example project:

```bash
# Clone the repository
git clone https://github.com/hleroy/django-signature-pad.git
cd django-signature-pad

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install Django and django-signature-pad package
pip install Django
pip install -e .

# Setup the example project
cd example_project
python manage.py migrate
python manage.py createsuperuser
```

Fill in the superuser information when prompted. Then start the development server:

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to see the demo in action. You can also access the [admin interface](http://127.0.0.1:8000/admin) using the credentials you just created.

## Knwown Issue

When using a ModelForm, specifying the custom width and height attributes in `Meta` doesn't work. It works using an inline field declaration though. If you can help fixing this issue, let me know.

```python
class MyModelForm(forms.ModelForm):
    # Works
    signature = forms.JSONField(
        widget=SignaturePadWidget(attrs={"width": 600, "height": 300})
    )

    class Meta:
        model = SignatureModel
        fields = ["signature"]
        # Doesn't work
        widgets = {
            'signature': SignaturePadWidget(attrs={'width': 600, 'height': 300})
        }
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
