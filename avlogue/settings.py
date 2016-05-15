"""
Avlogue settings.
"""
import os

from django.conf import settings


def get_avlogue_setting(name, default):
    return getattr(settings, 'AVLOGUE_{}'.format(name), default)

DIR = get_avlogue_setting('DIR', 'avlogue')

VIDEO_DIR = get_avlogue_setting('VIDEO_DIR', os.path.join(DIR, 'video'))
VIDEO_STREAMS_DIR = get_avlogue_setting('VIDEO_STREAMS_DIR', os.path.join(DIR, 'video', 'streams'))

AUDIO_DIR = get_avlogue_setting('AUDIO_DIR', os.path.join(DIR, 'audio'))
AUDIO_STREAMS_DIR = get_avlogue_setting('AUDIO_STREAMS_DIR', os.path.join(DIR, 'audio', 'streams'))

FFMPEG_OUTPUT_PATH = get_avlogue_setting('FFMPEG_OUTPUT_PATH', '/tmp/avlogue')
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
