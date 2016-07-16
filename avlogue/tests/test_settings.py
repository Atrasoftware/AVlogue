"""Settings that need to be set in order to run the tests."""
import logging
import os

DEBUG = True

logging.basicConfig(level=logging.DEBUG)

SITE_ID = 1

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'avlogue.tests.urls'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(APP_ROOT, '..', 'static')
MEDIA_ROOT = os.path.join(APP_ROOT, '..', 'test_media')

STATICFILES_DIRS = (
    os.path.join(APP_ROOT, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(APP_ROOT, 'tests/test_app/templates'),
)

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
]

INTERNAL_APPS = [
    'avlogue',
    'avlogue.tests.example_app'
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(APP_ROOT, 'tests', 'coverage')
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]
COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

SECRET_KEY = 'foobar'

BROKER_URL = 'memory://'
BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memory'

from .celery import *  # NOQA

AVLOGUE_TEMP_PATH = os.path.abspath(os.path.join(APP_ROOT, '..', 'test_avlogue_temp_path'))
AVLOGUE_FFMPEG_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffmpeg'
AVLOGUE_FFPROBE_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffprobe'
