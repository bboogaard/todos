"""
Django settings for todo project.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f2mm!+0q6of2^s(o3kahph*hr%s5a2j272=2h^uhjrlas%54k$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'todos.apps.TodosConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_media_fixtures',
    'crispy_forms',
    'private_storage',
    # Added.
    'haystack',
    'taggit',
    'easy_thumbnails',
    'widget_tweaks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lib.middleware.CronMiddleware'
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'todos.context_processors.settings',
                'todos.context_processors.wallpapers'
            ],
            'libraries': {
                'widgets': 'services.widgets.templatetags'
            }
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default='postgresql://postgres:@/todos')
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'todos_cache'
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR,'static')
STATIC_URL = '/static/'
# STATIC_URL = 'https://s3-ap-southeast-1.amazonaws.com/%s/static/' % AWS_S3_BUCKET_NAME

MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = "/media/"

PRIVATE_STORAGE_ROOT = '/private-media/'
PRIVATE_STORAGE_AUTH_FUNCTION = 'private_storage.permissions.allow_staff'

# Messagebird settings
MESSAGEBIRD_ACCESS_KEY = os.getenv('MESSAGEBIRD_ACCESS_KEY', 'test_7lxBEe1exwYBRwlr2eF6diV9u')
MESSAGEBIRD_RECIPIENTS = ['31646560853']
MESSAGEBIRD_MIN_AMOUNT = 1
MESSAGEBIRD_FROM_NAME = "Todo's"

X_FRAME_OPTIONS = 'SAMEORIGIN'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Search
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}
