# tests/test_settings.py

SECRET_KEY = "dummy-secret-key"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "signature_pad",
    "tests",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    },
]

# Use BigAutoField for primary keys if using Django >= 3.2
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
