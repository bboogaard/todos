import os

from app.settings import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

# Site url
SITE_ID = 1

SITE_URL = 'https://py-todos.nl'

STATIC_URL = 'https://py-todos.nl/static/'

STATIC_ROOT = '/home/bboogaard/media/py-todos/staticfiles'

MEDIA_ROOT = '/home/bboogaard/media/py-todos/media'

MEDIA_URL = 'https://py-todos.nl/media/'

DATABASES = {
    'default': dj_database_url.config('DATABASE_URL')
}

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
