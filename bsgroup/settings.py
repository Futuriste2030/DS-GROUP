"""
Django settings for bsgroup project.
BS GROUP — vitrine + apps metier (logiques a venir).
"""

from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-g!@sjrrs3rtx3ojjpq2n!ua(c58wa!(j9-lj8iweyhe%9$ke2u')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,testserver', cast=Csv())

# CSRF trusted origins (requis en prod derrière reverse proxy HTTPS)
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Domaine canonique unique pour le SEO (sitemap, canonical, hreflang) — même logique que DIGI-AGENCY.
CANONICAL_DOMAIN = config('CANONICAL_DOMAIN', default='bsgroup.ml')

# Security headers production (derrière Nginx HTTPS)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000 if not DEBUG else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=not DEBUG, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'SAMEORIGIN'


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'imagekit',
    'ckeditor',
    # Core + apps metier BS GROUP (même logique que DIGI-AGENCY)
    'core',
    'main',
    'services',
    'team',
    'projects',
    'blog',
    'careers',
    'contact',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.CookieConsentMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ComingSoonMiddleware',
]

ROOT_URLCONF = 'bsgroup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Templates centralises : templates/<app>/*.html
        # (phase 2 : factorisation base.html a venir).
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.get_site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'bsgroup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

import dj_database_url

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        cast=dj_database_url.parse
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization — même logique que DIGI-AGENCY (FR par défaut, sans préfixe)

LANGUAGE_CODE = 'fr'
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('ar', 'العربية'),
]
MODELTRANSLATION_DEFAULT_LANGUAGE = 'fr'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr',)
MODELTRANSLATION_LANGUAGES = ('fr', 'en', 'ar')

TIME_ZONE = 'Africa/Bamako'

USE_I18N = True

USE_TZ = True

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365

LOCALE_PATHS = [BASE_DIR / 'locale']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email — même logique que DIGI (console en dev, SMTP via env en prod)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@bsgroup.ml')
EMAIL_FROM_NAME = config('EMAIL_FROM_NAME', default='BS GROUP')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='contact@bsgroup.ml')
CAREERS_EMAIL = config('CAREERS_EMAIL', default='careers@bsgroup.ml')
HR_EMAIL = config('HR_EMAIL', default=CAREERS_EMAIL)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Chatbot (Gemini) — même logique que DIGI-AGENCY (RAG sur contenus DB + clé via .env)
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-3.6-flash')
CHAT_MAX_MESSAGE_LEN = config('CHAT_MAX_MESSAGE_LEN', default=2000, cast=int)
CHAT_MAX_HISTORY = config('CHAT_MAX_HISTORY', default=6, cast=int)
CHAT_MAX_CONTEXT_CHARS = config('CHAT_MAX_CONTEXT_CHARS', default=4000, cast=int)
CHAT_RATE_LIMIT_MIN = config('CHAT_RATE_LIMIT_MIN', default=12, cast=int)

# Consentement cookies — ID stable first-party + preuve RGPD (même logique que DIGI-AGENCY)
COOKIE_POLICY_VERSION = config('COOKIE_POLICY_VERSION', default='1.0')
CONSENT_COOKIE_NAME = 'consent_id'
# 13 mois max (CNIL) pour le cookie ID ; expiry du choix local gérée en JS (6 mois).
CONSENT_COOKIE_AGE = 60 * 60 * 24 * 395
# Rétention preuves consentement (CNIL : 6 mois) — commande cleanup_consents.
CONSENT_RETENTION_DAYS = config('CONSENT_RETENTION_DAYS', default=182, cast=int)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files storage (WhiteNoise compression + manifest pour cache busting)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# WhiteNoise config
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = not DEBUG
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0

# ImageKit — conversion automatique WebP + optimisation
IMAGEKIT_DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
IMAGEKIT_CACHEFILE_DIR = 'uploads/cache'
IMAGEKIT_CACHEFILE_NAMER = 'imagekit.cachefiles.namers.source_name_as_path'

# CKEditor 5 — configuration pour champs riches (blog, projets)
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'strikethrough',
            '|', 'link', 'bulletedList', 'numberedList', 'blockQuote',
            '|', 'insertTable', 'mediaEmbed', '|', 'undo', 'redo'
        ],
        'language': 'fr',
        'htmlSupport': {
            'allow': [
                {'name': '/.*/', 'attributes': True, 'classes': True, 'styles': True}
            ]
        },
    },
    'minimal': {
        'toolbar': ['bold', 'italic', 'link', 'bulletedList', 'numberedList', 'undo', 'redo'],
        'language': 'fr',
    }
}
