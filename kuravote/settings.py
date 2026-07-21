from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url
from django.core.management.utils import get_random_secret_key

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_otp',
    'django_otp.plugins.otp_totp',

    # Our app
    'election',
]

MIDDLEWARE = [
    # compresses responses for faster load times
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'election.admin_2fa.AdminOTPMiddleware',
    # CORRECT — points to election/middleware.py
    'election.middleware.ForcePasswordChangeMiddleware',
]

ROOT_URLCONF = 'kuravote.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'election.utils.active_election',  # custom context processor for active election
            ],
        },
    },
]

WSGI_APPLICATION = 'kuravote.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,  # Increased timeout
            'isolation_level': 'IMMEDIATE',
            'init_command': "PRAGMA synchronous = OFF; PRAGMA journal_mode = WAL;",
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Switch between local MySQL and Render PostgreSQL
if os.environ.get('DATABASE_URL'):
    # Render (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
        )
    }
else:
    #     # Connection pooling — reuse DB connections instead of
    #     # creating a new one per request
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     os.getenv('DB_NAME'),
            'USER':     os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST':     os.getenv('DB_HOST', default='localhost'),
            'PORT':     os.getenv('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'connect_timeout': 10,
            },
            'CONN_MAX_AGE': 60,  # ← Keep DB connections alive for 60s
            #   instead of closing after each request
        }
    }

# ─── Custom Auth ─────────────────────────────────────────
# Tells Django to use our custom Student model for auth
AUTH_USER_MODEL = 'election.Student'


AUTHENTICATION_BACKENDS = [
    'election.backends.AdmissionNumberBackend',  # student login
    'django.contrib.auth.backends.ModelBackend',  # admin login
]
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# settings.py — lower cost factor only for bulk-imported default passwords
# Students must change on first login anyway, so the default password
# security level matters less than the changed password.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# ─── Session Security ────────────────────────────────────
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# Set these properly based on environment
SESSION_COOKIE_SECURE = not DEBUG          # True in production
CSRF_COOKIE_SECURE = not DEBUG

# ─── Security Headers ────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
X_FRAME_OPTIONS = 'DENY'

# ─── Content Security Policy (add django-csp to requirements) ──
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
    "https://fonts.googleapis.com",
    "'unsafe-inline'",     # Bootstrap requires this; tighten later
)
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:")
CSP_FRAME_ANCESTORS = ("'none'",)


# ─── Security Headers ────────────────────────────────────
CSRF_COOKIE_HTTPONLY = False       # needed for JS form submits
X_FRAME_OPTIONS = 'DENY'      # prevent clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True


# ─── Login / Logout Redirects ────────────────────────────
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Eager loading — serve compressed static files
STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# for production collectstatic
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'ERROR',
        },
    },
}


if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─── Cache (for live results speed) ─────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'kuravote-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}


VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_EMAIL = os.environ.get('VAPID_EMAIL')

# For development only - generate temporary keys if missing
if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
    from pywebpush import generate_vapid_keys
    keys = generate_vapid_keys()
    VAPID_PRIVATE_KEY = keys['private']
    VAPID_PUBLIC_KEY = keys['public']
    print(f" Generated temporary VAPID keys. Set them in environment for production.")

# File upload limits — increase for large CSVs
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520   # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520   # 20MB

# Increase timeout for large uploads
DATA_UPLOAD_MAX_NUMBER_FIELDS = 6000240
