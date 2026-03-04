"""Django settings for the news_project application.

This settings file supports both local development (with a virtual environment)
and containerised deployment (Docker). Sensitive values are read from
environment variables so they are never hard-coded or committed to version
control.

For development, copy ``secrets.example.txt`` to ``.env`` (or set the
variables in your shell) before running the server.

Environment variables recognised
---------------------------------
``DJANGO_SECRET_KEY``
    Django secret key. **Required in production.**
    Defaults to an insecure development key — change this before deploying.
``DJANGO_DEBUG``
    Set to ``"false"`` in production. Defaults to ``"true"`` for development.
``DJANGO_ALLOWED_HOSTS``
    Comma-separated list of allowed hostnames, e.g. ``"localhost,127.0.0.1"``.
``DB_ENGINE``
    Django database engine. Defaults to MySQL. Set to
    ``"django.db.backends.sqlite3"`` for lightweight testing.
``DB_NAME``
    Database name (MySQL) or file path (SQLite). Defaults to ``"news_app_db"``.
``DB_USER``
    Database username. Defaults to ``"news_user"``.
``DB_PASSWORD``
    Database password. Defaults to empty string — set this via env var.
``DB_HOST``
    Database host. Defaults to ``"localhost"``.
``DB_PORT``
    Database port. Defaults to ``"3306"`` (MySQL).
``X_API_URL``
    X (Twitter) API endpoint URL for posting tweets.
``X_API_TOKEN``
    Bearer token for the X API.
"""

import os
from pathlib import Path

# ── Base directory ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key-replace-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() != "false"

_allowed = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]

# ── Installed apps ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "news_app.apps.NewsAppConfig",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "news_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "news_project.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
# Defaults to MySQL. Override DB_ENGINE to "django.db.backends.sqlite3" and
# DB_NAME to a file path for SQLite (useful inside Docker without MySQL).
_db_engine = os.environ.get("DB_ENGINE", "django.db.backends.mysql")
_db_name = os.environ.get("DB_NAME", "news_app_db")

if _db_engine == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": _db_engine,
            "NAME": BASE_DIR / _db_name,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": _db_engine,
            "NAME": _db_name,
            "USER": os.environ.get("DB_USER", "news_user"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "news_app.CustomUser"

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = "static/"

# ── Email ─────────────────────────────────────────────────────────────────────
# Console backend is suitable for development. In production, replace with
# SMTP or a third-party service backend.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@example.com"

# ── X (Twitter) API ───────────────────────────────────────────────────────────
# Set these via environment variables — never hard-code credentials.
X_API_URL = os.environ.get("X_API_URL", "https://api.twitter.com/2/tweets")
X_API_TOKEN = os.environ.get("X_API_TOKEN", "")

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}
