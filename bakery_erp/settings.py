"""
Django settings for bakery_erp project — Railway production-ready.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-#8dh8-hxh*8j93l2k@dfu8n1rr@s2-tyezw9-iw33g1@y)bgoa'
)

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'mybakeryerp-production.up.railway.app',
    '.railway.app',
    'testserver',
]

CSRF_TRUSTED_ORIGINS = [
    'https://mybakeryerp-production.up.railway.app',
    'https://*.railway.app',
]

# Production security headers (Railway HTTPS orqali ishlaydi)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ── Apps ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'production',
    'sales',
    'branches',
    'accounting',
    'hr',
    'rosetta',
    'whitenoise.runserver_nostatic',
    'whitenoise',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bakery_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_roles',
                'core.context_processors.menu_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'bakery_erp.wsgi.application'

# ── Database ─────────────────────────────────────────────────────────────────
# SQLite — Railway'da db.sqlite3 git orqali yuklanadi
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization ──────────────────────────────────────────────────────
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('uz', _('Uzbek (Latin)')),
    ('uz-cyrl', _('Uzbek (Kirill)')),
    ('ru', _('Russian')),
]

LANGUAGE_CODE = 'uz'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ── Telegram Bot ──────────────────────────────────────────────────────────────
# Railway environment variables dan o'qiladi
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
