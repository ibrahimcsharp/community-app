"""
Settings for the Community API.

Values you are likely to change (database login, secret key, frontend URL)
are read from environment variables or from a `.env` file next to manage.py.
See `.env.example` for the full list. Defaults match a fresh XAMPP install.
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # the "backend" folder


# ---------------------------------------------------------------------
# Read backend/.env (simple KEY=VALUE lines) if the file exists.
# Real environment variables win over the file.
# ---------------------------------------------------------------------
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


# ---------------------------------------------------------------------
# Basics
# ---------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-key-change-me-before-going-live")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    # Django's built-in login system (passwords, user model support)
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Our apps
    "accounts",    # users: register, login, profile
    "community",   # categories, posts, comments
    "moderation",  # admin-only: approve / reject / block
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be first: adds CORS headers
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEST_RUNNER = "config.test_runner.TestRunner"


# ---------------------------------------------------------------------
# Database (MySQL / MariaDB from XAMPP)
# The tables are created by database/community_db.sql, not by Django.
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "community_db"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            # Strict mode: too-long text is an error instead of being silently cut off.
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Store plain local date/times, the same way MySQL's NOW() does.
USE_TZ = False


# ---------------------------------------------------------------------
# Users and passwords
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"  # our own users table instead of Django's

# Rules checked when someone registers or changes their password.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------
# Django REST Framework + JWT
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    # Every request is checked for an "Authorization: Bearer <token>" header.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # By default you must be logged in. Views that are open say so themselves.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Only JSON in and out.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # sent with every request
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # used to get a new access token
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ---------------------------------------------------------------------
# CORS: which websites may call this API from the browser
# ---------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.environ.get(
    "FRONTEND_URLS", "http://localhost:4200,http://127.0.0.1:4200"
).split(",")
