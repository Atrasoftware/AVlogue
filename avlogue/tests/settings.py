"""
These settings are used by the ``manage.py`` command.

With normal tests we want to use the fastest possible way which is an
in-memory sqlite database but if you want to create South migrations you
need a persistant database.

Unfortunately there seems to be an issue with either South or syncdb so that
defining two routers ("default" and "south") does not work.

"""
import os

from .test_settings import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

MEDIA_ROOT = os.path.join(APP_ROOT, '..', 'media')  # NOQA
AVLOGUE_FFMPEG_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.0.2/bin/ffmpeg'
AVLOGUE_FFPROBE_EXECUTABLE = '/usr/local/Cellar/ffmpeg/3.0.2/bin/ffprobe'
