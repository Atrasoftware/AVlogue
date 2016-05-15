"""
Avlogue models.
"""
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from avlogue import managers
from avlogue import settings

name_regex_validator = RegexValidator(regex='^[a-z0-9_-]+$',
                                      message='Use only plain lowercase letters (ASCII), numbers and '
                                              'underscores.')


class AudioFields(models.Model):
    """
    Audio fields.
    """
    audio_codec = models.CharField(_('audio codec'), max_length=20)
    audio_bitrate = models.PositiveIntegerField(_('audio bitrate'), default=0)
    audio_channels = models.PositiveIntegerField(_('audio channels'), blank=True, null=True)

    class Meta:
        abstract = True


class VideoFields(AudioFields):
    """
    Video file fields, also contains audio fields.
    """
    video_codec = models.CharField(_('video codec'), max_length=20)
    video_bitrate = models.PositiveIntegerField(_('video bitrate'), default=0)
    video_width = models.IntegerField(_('video width'), blank=True, null=True)
    video_height = models.IntegerField(_('video height'), blank=True, null=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class BaseFormat(models.Model):
    """
    Base encode format.
    """
    name = models.CharField(_('name'), unique=True, max_length=40, validators=[name_regex_validator])
    container = models.CharField(_('container format'), max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AudioFormat(BaseFormat, AudioFields):
    """
    Audio encode format.
    """
    audio_codec_params = models.CharField(_('audio codec params'), max_length=400, blank=True)

    class Meta:
        verbose_name = _('audio format')
        verbose_name_plural = _('audio formats')


class VideoFormat(BaseFormat, VideoFields):
    """
    Video encode format.
    """
    audio_codec_params = models.CharField(_('audio codec params'), max_length=400, blank=True)
    video_codec_params = models.CharField(_('video codec params'), max_length=400, blank=True)
    video_aspect_mode = models.CharField(
        _('video aspect mode'),
        max_length=10,
        choices=(('scale', _('scale')), ('scale_crop', _('scale and crop'))),
        default='scale',
        help_text=_('Aspect mode is only used if both video width and height sizes are specified,'
                    'otherwise aspect mode will be ignored.'))

    class Meta:
        verbose_name = _('video format')
        verbose_name_plural = _('video formats')


@python_2_unicode_compatible
class BaseFormatSet(models.Model):
    name = models.CharField(_('name'), max_length=40, validators=[name_regex_validator])

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AudioFormatSet(BaseFormatSet):
    """
    Set of audio formats.
    """
    formats = models.ManyToManyField(AudioFormat, verbose_name=_('formats'))


class VideoFormatSet(BaseFormatSet):
    """
    Set of video formats.
    """
    formats = models.ManyToManyField(VideoFormat, verbose_name=_('formats'))


@python_2_unicode_compatible
class MediaFile(models.Model):
    """
    Base media file model.
    """
    bitrate = models.PositiveIntegerField(_('average file bitrate'))
    duration = models.FloatField(_('duration'))
    size = models.PositiveIntegerField(_('size'))

    def format_has_lower_quality(self, encode_format):
        raise NotImplementedError  # pragma: no cover

    def convert(self, format_set):
        from avlogue import tasks
        format_set = filter(self.format_has_lower_quality, format_set.formats.all())
        return tasks.encode_media_file.delay(self, format_set)

    def __str__(self):
        # FIXME: undefined file prop
        return self.file.name

    class Meta:
        abstract = True


class AudioFile(MediaFile, AudioFields):
    """
    Uploaded audio file.
    """
    objects = managers.AudioFileQuerySet.as_manager()

    file = models.FileField(_('file'), upload_to=settings.AUDIO_DIR)

    def format_has_lower_quality(self, encode_format):
        """
        Return True if encode_format has a lower quality than current audio params.
        :param encode_format:
        :return:
        """
        bitrate = self.audio_bitrate or self.bitrate
        return bitrate >= encode_format.audio_bitrate


class VideoFile(MediaFile, VideoFields):
    """
    Uploaded video file.
    """
    objects = managers.VideoFileQuerySet.as_manager()

    file = models.FileField(_('file'), upload_to=settings.VIDEO_DIR)

    def format_has_lower_quality(self, encode_format):
        """
        Return True if encode_format has a lower quality than current video params.
        :param encode_format:
        :return:
        """
        audio_bitrate = self.audio_bitrate or self.bitrate
        video_bitrate = self.video_bitrate or self.bitrate

        return audio_bitrate >= encode_format.audio_bitrate \
            and video_bitrate >= encode_format.video_bitrate


@python_2_unicode_compatible
class BaseStream(models.Model):

    size = models.PositiveIntegerField(_('size'))

    def __str__(self):
        return "{}: {}".format(str(self.format), str(self.media_file))

    class Meta:
        abstract = True


class AudioStream(BaseStream):
    """
    Audio file stream.
    """
    file = models.FileField(_('stream file'), upload_to=settings.AUDIO_STREAMS_DIR)
    media_file = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name='streams')
    format = models.ForeignKey(AudioFormat)

    class Meta:
        unique_together = ['media_file', 'format']


class VideoStream(BaseStream):
    """
    Video file stream.
    """
    file = models.FileField(_('stream file'), upload_to=settings.VIDEO_STREAMS_DIR)
    media_file = models.ForeignKey(VideoFile, on_delete=models.CASCADE, related_name='streams')
    format = models.ForeignKey(VideoFormat)

    class Meta:
        unique_together = ['media_file', 'format']


def delete_media_file_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


def delete_media_old_file_on_model_change(sender, instance, **kwargs):
    if instance.pk is not None:
        instance = sender.objects.filter(pk=instance.pk).first()
        if instance is not None:
            instance.file.delete(save=False)


# Register media files deletion on model deletion
receiver(models.signals.post_delete, sender=VideoFile)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=VideoStream)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=AudioFile)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=AudioStream)(delete_media_file_on_model_delete)

# Register media files deletion on model changing
receiver(models.signals.pre_save, sender=VideoFile)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=VideoStream)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=AudioFile)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=AudioStream)(delete_media_old_file_on_model_change)
