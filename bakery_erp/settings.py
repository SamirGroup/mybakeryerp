"""
Django settings for bakery_erp project — Railway/Render production-ready.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    '0tynt^-cd#o^)oxz*kdz#v51^2t-&o(1apepdi%s&!1qp9f^847jid=i!e5f0_@-'
)

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Railway va Render uchun barcha hostlar
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'testserver',
    # Railway
    'mybakeryerp-production.up.railway.app',
    '.railway.app',
    # Render
    '.onrender.com',
    '.render.com',
    # RAILWAY_PUBLIC_DOMAIN env var bo'lsa qo'shish
] + [h for h in [os.getenv('RAILWAY_PUBLIC_DOMAIN', ''), os.getenv('RENDER_EXTERNAL_HOSTNAME', '')] if h]

CSRF_TRUSTED_ORIGINS = [
    'https://mybakeryerp-production.up.railway.app',
    'https://*.railway.app',
    'https://*.onrender.com',
    'https://*.render.com',
]

# Production security (Railway/Render HTTPS'ni o'zi boshqaradi)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ── Apps ──────────────────────────────────────────────────────────────────────
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

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASE_URL bo'lsa PostgreSQL ishlatish (Railway/Render)
if os.getenv('DATABASE_URL'):
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            env='DATABASE_URL',
            conn_max_age=600,
            ssl_require=True,
        )
    except ImportError:
        pass  # dj-database-url o'rnatilmagan bo'lsa SQLite ishlatiladi

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
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ── Telegram Bot (doimiy qiymatlar) ──────────────────────────────────────────
# Ustunlik: DB (admin panel) > env var > shu yergi default
TELEGRAM_BOT_TOKEN = os.getenv(
    'TELEGRAM_BOT_TOKEN',
    '8306874742:AAEhMFKCfniNI4XkpYR8IfJ4fHBiUsVwNv0'
)
TELEGRAM_CHAT_ID = os.getenv(
    'TELEGRAM_CHAT_ID',
    '-1002064363271'
)
