"""
AVlogue settings.
"""
import os
import shutil

from django.conf import settings
from django.core.files.storage import default_storage


def which(cmd):
    """
    Return the path to an executable which would be run if the given cmd was called.
    If no cmd would be called, return None.

    :param cmd:
    :return:
    """
    if hasattr(shutil, 'which'):
        return shutil.which(cmd)
    else:

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(cmd)
        if fpath:
            if is_exe(cmd):
                return cmd
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, cmd)
                if is_exe(exe_file):
                    return exe_file

        return None


def get_avlogue_setting(name, default):
    return getattr(settings, 'AVLOGUE_{}'.format(name), default)


#: Base AVlogue directory.
DIR = get_avlogue_setting('DIR', 'avlogue')

#: Video files directory.
VIDEO_DIR = get_avlogue_setting('VIDEO_DIR', os.path.join(DIR, 'video'))

#: Video streams directory.
VIDEO_STREAMS_DIR = get_avlogue_setting('VIDEO_STREAMS_DIR', os.path.join(VIDEO_DIR, 'streams'))

#: Audio files directory.
AUDIO_DIR = get_avlogue_setting('AUDIO_DIR', os.path.join(DIR, 'audio'))

#: Audio streams directory.
AUDIO_STREAMS_DIR = get_avlogue_setting('AUDIO_STREAMS_DIR', os.path.join(AUDIO_DIR, 'streams'))

#: Temporary path for conversation task.
TEMP_PATH = get_avlogue_setting('TEMP_PATH', '/tmp/avlogue')
if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)

assert os.access(TEMP_PATH, os.W_OK), 'AVlogue must have write access into `{}` temporary path'.format(TEMP_PATH)

#: Path to ffmpeg executable.
FFMPEG_EXECUTABLE = get_avlogue_setting('FFMPEG_EXECUTABLE', 'ffmpeg')

#: Path to ffprobe executable.
FFPROBE_EXECUTABLE = get_avlogue_setting('FFPROBE_EXECUTABLE', 'ffprobe')

assert which(FFMPEG_EXECUTABLE) is not None, "ffmpeg `{}` was not found.".format(FFMPEG_EXECUTABLE)
assert which(FFPROBE_EXECUTABLE) is not None, "ffprobe `{}` was not found.".format(FFMPEG_EXECUTABLE)

#: Video codecs. Key is a human name, value is a encoder library.
VIDEO_CODECS = get_avlogue_setting('VIDEO_CODECS', {
    # name  # library
    'h264': 'libx264',
    'vp8': 'libvpx',
    'mpeg4': 'mpeg4',
    'theora': 'libtheora'
})

#: Video containers. Key is a file extension, value is a encoder container name.
VIDEO_CONTAINERS = get_avlogue_setting('VIDEO_CONTAINERS', {
    # ext  # name
    'mkv': 'matroska',
    'webm': 'webm',
    'avi': 'avi',
    'flv': 'flv',
    'mp4': 'mp4',
    'ogv': 'ogg',
    '3gp': '3gp'
})

#: Audio codecs. Key is a human name, value is a encoder library.
AUDIO_CODECS = get_avlogue_setting('AUDIO_CODECS', {
    # name  # library
    'mp3': 'libmp3lame',
    'aac': 'aac',
    'vorbis': 'libvorbis',
    'ac3': 'ac3',
    'pcm_f32le': 'pcm_f32le',
    'pcm_s16be': 'pcm_s16be'
})

#: Video containers. Key is a file extension, value is a encoder container name.
AUDIO_CONTAINERS = get_avlogue_setting('AUDIO_CONTAINERS', {
    # ext  # name
    'mp3': 'mp3',
    'ac3': 'ac3',
    'wav': 'wav',
    'aiff': 'aiff',
    'ogg': 'ogg',
    'aac': 'adts'
})

#: Audio/Video files storage.
MEDIA_STORAGE = get_avlogue_setting('MEDIA_FILE_STORAGE', default_storage)

#: Audio/Video streams storage.
MEDIA_STREAMS_STORAGE = get_avlogue_setting('MEDIA_STREAMS_STORAGE', default_storage)

#: Video preview image size.  If you'd like to keep the aspect ratio, you need to specify only one component,
#: either width or height, and set the other component to -1.
VIDEO_PREVIEW_SIZE = get_avlogue_setting('VIDEO_PREVIEW_SIZE', '-1:250')
