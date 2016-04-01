"""
Avlogue models.
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AudioFormat(models.Model):
    """
    Single audio format.
    """
    name = models.CharField(_('name'), unique=True, max_length=40)
    codec = models.CharField(_('codec'), max_length=20)
    bitrate = models.PositiveIntegerField(_('bitrate'))
    channels = models.PositiveIntegerField(_('channels'), blank=True, null=True)
    container = models.CharField(_('container format'), max_length=10)


class VideoFormat(models.Model):
    """
    Single video format.
    """
    name = models.CharField(_('name'), unique=True, max_length=40)
    video_codec = models.CharField(_('video codec'), max_length=20)
    video_profile = models.CharField(_('video profile'), max_length=20)
    video_bitrate = models.PositiveIntegerField(_('video bitrate'))
    video_resolution = models.CharField(_('video resolution'), max_length=20)

    audio_codec = models.CharField(_('audio codec'), max_length=20)
    audio_bitrate = models.PositiveIntegerField(_('audio bitrate'))
    audio_channels = models.PositiveIntegerField(_('audio channels'), blank=True, null=True)
    container = models.CharField(_('container format'), max_length=10)


class AudioFormSet(models.Model):
    """
    Set of audio formats.
    """
    name = models.CharField(_('name'), max_length=40)
    formats = models.ManyToManyField(AudioFormat, verbose_name=_('formats'))


class VideoFormSet(models.Model):
    """
    Set of video formats.
    """
    name = models.CharField(_('name'), max_length=40)
    formats = models.ManyToManyField(VideoFormat, verbose_name=_('formats'))


class AudioFile(models.Model):
    """
    Uploaded audio file.
    """
    source_file = models.FileField(_('source file'))

    codec = models.CharField(_('codec'), max_length=20)
    bitrate = models.PositiveIntegerField(_('bitrate'))
    length = models.PositiveIntegerField(_('length'))
    container = models.CharField(_('container format'), max_length=10)


class VideoFile(models.Model):
    """
    Uploaded video file.
    """
    source_file = models.FileField(_('source file'))

    codec = models.CharField(_('codec'), max_length=20)
    bitrate = models.PositiveIntegerField(_('bitrate'))
    resolution = models.PositiveIntegerField(_('resolution'))
    length = models.PositiveIntegerField(_('length'))
    container = models.CharField(_('container format'), max_length=10)
