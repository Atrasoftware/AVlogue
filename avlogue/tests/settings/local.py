"""
These settings are used by the ``manage.py`` command.

With normal tests we want to use the fastest possible way which is an
in-memory sqlite database but if you want to create South migrations you
need a persistant database.

Unfortunately there seems to be an issue with either South or syncdb so that
defining two routers ("default" and "south") does not work.

"""
import djcelery

from avlogue.tests.settings.base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

djcelery.setup_loader()

INSTALLED_APPS += ('djcelery',)

BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_CACHE_BACKEND = 'djcelery.backends.cache:CacheBackend'
CELERY_SEND_EVENTS = True
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

MEDIA_ROOT = os.path.join(APP_ROOT, '..', 'media')  # NOQA

AVLOGUE_FFMPEG_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffmpeg'
AVLOGUE_FFPROBE_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.1.1/bin/ffprobe'
