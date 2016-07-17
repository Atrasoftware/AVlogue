"""Settings that need to be set in order to run the tests."""
from __future__ import absolute_import

from celery import Celery

from avlogue.tests.settings.base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_ROOT = os.path.join(APP_ROOT, '..', 'test_media')

BROKER_URL = 'memory://'
BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memory'

app = Celery('avlogue')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: INSTALLED_APPS)

AVLOGUE_TEMP_PATH = os.path.abspath(os.path.join(APP_ROOT, '..', 'test_avlogue_temp_path'))
AVLOGUE_FFMPEG_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffmpeg'
AVLOGUE_FFPROBE_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffprobe'
