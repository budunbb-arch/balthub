import os
from pathlib import Path
from urllib.parse import quote as urlquote
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'balthub.rf39.ru',
    'квартирукупить.рф',
    'xn--b1afkwdgk7a.xn--p1ai',
    '212.192.0.71',
    '*.cloudflare.com',
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    "https://balthub.rf39.ru",
    "https://квартирукупить.рф",
    "https://xn--b1afkwdgk7a.xn--p1ai",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'apps.core',
    'apps.core.common',
    'apps.estates',
    'apps.estates.developers',
    'apps.estates.parsing',
    'apps.estates.projects',
    'apps.estates.houses',
    'apps.estates.flats',
    'apps.estates.tags',
    'apps.core.dictionaries',
    'apps.parsing_section',
    'django_celery_beat',
    'apps.modules.apps.ModulesConfig',
    'apps.leads',
    'apps.maps',
    'apps.core.documents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'apps.core.middleware.language.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.view_name.ViewNameMiddleware',
    'apps.core.middleware.site_status.SiteStatusMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'apps.core.engines.context_processors.layout_modules',
    'apps.core.engines.context_processors.breadcrumbs',
    'apps.core.engines.context_processors.seo',
    'apps.core.engines.context_processors.localization',
    'apps.core.engines.context_processors.map_settings',
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Kaliningrad'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [ 
    BASE_DIR / "static"
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

WHITENOISE_SKIP_COMPRESS = (
    lambda path: path.endswith((".woff", ".woff2", ".ttf")),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'
FEEDS_DIR = BASE_DIR / "feeds"


REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{urlquote(REDIS_PASSWORD, safe='')}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

CACHE_TTL = 60 * 10

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Yandex Maps secret_key: pXYYru0Js2EhZk_QEqtMFg==
