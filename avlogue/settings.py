"""
AVlogue settings.
"""
import os

from django.conf import settings
from django.core.files.storage import default_storage


def get_avlogue_setting(name, default):
    return getattr(settings, 'AVLOGUE_{}'.format(name), default)


DIR = get_avlogue_setting('DIR', 'avlogue')

VIDEO_DIR = get_avlogue_setting('VIDEO_DIR', os.path.join(DIR, 'video'))
VIDEO_STREAMS_DIR = get_avlogue_setting('VIDEO_STREAMS_DIR', os.path.join(DIR, 'video', 'streams'))

AUDIO_DIR = get_avlogue_setting('AUDIO_DIR', os.path.join(DIR, 'audio'))
AUDIO_STREAMS_DIR = get_avlogue_setting('AUDIO_STREAMS_DIR', os.path.join(DIR, 'audio', 'streams'))

TEMP_PATH = get_avlogue_setting('TEMP_PATH', '/tmp/avlogue')
if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)

FFMPEG_EXECUTABLE = get_avlogue_setting('FFMPEG_EXECUTABLE', 'ffmpeg')
FFPROBE_EXECUTABLE = get_avlogue_setting('FFPROBE_EXECUTABLE', 'ffprobe')

VIDEO_CODECS = get_avlogue_setting('VIDEO_CODECS', {
    'h264': 'libx264',
    'vp8': 'libvpx',
    'mpeg4': 'mpeg4'
})

VIDEO_CONTAINERS = get_avlogue_setting('VIDEO_CONTAINERS', {
    'mkv': 'matroska',
    'webm': 'webm',
    'avi': 'avi',
    'flv': 'flv',
    'mp4': 'mp4',
})

AUDIO_CODECS = get_avlogue_setting('AUDIO_CODECS', {
    'mp3': 'libmp3lame',
    'aac': 'libfdk_aac',
    'vorbis': 'libvorbis',
    'ac3': 'ac3',
    'pcm_f32le': 'pcm_f32le',
    'pcm_s16be': 'pcm_s16be',
})

AUDIO_CONTAINERS = get_avlogue_setting('AUDIO_CONTAINERS', {
    'mp3': 'mp3',
    'ac3': 'ac3',
    'wav': 'wav',
    'aiff': 'aiff',
    'ogg': 'ogg',
})


MEDIA_STORAGE = get_avlogue_setting('MEDIA_FILE_STORAGE', default_storage)
MEDIA_STREAMS_STORAGE = get_avlogue_setting('MEDIA_STREAMS_STORAGE', default_storage)
