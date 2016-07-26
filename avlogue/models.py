"""
AVlogue models.
"""
import logging
import os

from celery.result import AsyncResult
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.six import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from avlogue import managers
from avlogue import settings
from avlogue import tasks
from avlogue.encoders import default_encoder
from avlogue.encoders.exceptions import GetFileInfoError
from avlogue.mime import mimetypes
from avlogue import utils

logger = logging.getLogger('avlogue')

video_file_validator = utils.ContentTypeValidator((r'video/.*',), message=_('Only video files are allowed.'))
audio_file_validator = utils.ContentTypeValidator((r'audio/.*',), message=_('Only audio files are allowed.'))


class AudioFields(models.Model):
    """
    Audio fields.
    """
    audio_codec = models.CharField(_('audio codec'), max_length=20, null=True,
                                   choices=((name, name) for name in settings.AUDIO_CODECS.keys()))
    audio_bitrate = models.PositiveIntegerField(_('audio bitrate'), null=True, blank=True)
    audio_channels = models.PositiveIntegerField(_('audio channels'), blank=True, null=True)

    class Meta:
        abstract = True


class VideoFields(AudioFields):
    """
    Video fields, also contains audio fields.
    """
    video_codec = models.CharField(_('video codec'), max_length=20, null=True,
                                   choices=((name, name) for name in settings.VIDEO_CODECS.keys()))
    video_bitrate = models.PositiveIntegerField(_('video bitrate'), null=True, blank=True)
    video_width = models.IntegerField(_('video width'), blank=True, null=True)
    video_height = models.IntegerField(_('video height'), blank=True, null=True)

    @property
    def resolution(self):
        video_width = self.video_width or ''
        video_height = self.video_height or ''
        if video_width or video_height:
            return '{}x{}'.format(video_width, video_height)

    class Meta:
        abstract = True


class MetaDataFields(models.Model):
    """
    Meta data fields.
    """
    bitrate = models.PositiveIntegerField(_('average file bitrate'), null=True, blank=True)
    duration = models.FloatField(_('duration'), null=True, blank=True)
    size = models.PositiveIntegerField(_('file size'), null=True, blank=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class BaseFormat(models.Model):
    """
    Base encode format.
    """
    name = models.CharField(_('name'), unique=True, max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AudioFormat(BaseFormat, AudioFields):
    """
    Audio encode format.
    """
    container = models.CharField(_('container format'), max_length=10,
                                 choices=((ext, name) for ext, name in settings.AUDIO_CONTAINERS.items()))
    audio_codec_params = models.CharField(_('audio codec params'), max_length=400, blank=True,
                                          help_text=_('Raw options to configure a selected audio codec'))

    class Meta:
        verbose_name = _('audio format')
        verbose_name_plural = _('audio formats')


class VideoFormat(BaseFormat, VideoFields):
    """
    Video encode format.
    """
    container = models.CharField(_('container format'), max_length=10,
                                 choices=((ext, name) for ext, name in settings.VIDEO_CONTAINERS.items()))
    audio_codec_params = models.CharField(_('audio codec params'), max_length=400, blank=True,
                                          help_text=_('Raw options to configure a selected audio codec'))
    video_codec_params = models.CharField(_('video codec params'), max_length=400, blank=True,
                                          help_text=_('Raw options to configure a selected video codec'))
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
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AudioFormatSet(BaseFormatSet):
    """
    Set of audio formats.
    """
    formats = models.ManyToManyField(AudioFormat, verbose_name=_('audio formats'), related_name='format_sets')


class VideoFormatSet(BaseFormatSet):
    """
    Set of video formats.
    """
    formats = models.ManyToManyField(VideoFormat, verbose_name=_('formats'), related_name='format_sets')


class FileChangedMixin(object):
    """
    Mixin adds logic to check whether file was changed and to update info.
    """
    def __init__(self, *args, **kwargs):
        super(FileChangedMixin, self).__init__(*args, **kwargs)
        if self.pk is not None:
            self._old_file = self.file
        else:
            self._old_file = None

    @property
    def file_changed(self):
        return self._old_file != self.file

    def clear_fields(self):
        fields = []
        if isinstance(self, MetaDataFields):
            fields.extend(MetaDataFields._meta.get_fields())
        if isinstance(self, VideoFields):
            fields.extend(VideoFields._meta.get_fields())
        if isinstance(self, AudioFields):
            fields.extend(AudioFields._meta.get_fields())
        for field in fields:
            setattr(self, field.name, None)

    def update_file_info(self):
        if self.file.name:
            stream_type = 'audio' if isinstance(self, (Audio, AudioStream)) else None
            with utils.get_local_file_path(self.file.file) as file_path:
                file_info = default_encoder.get_file_info(file_path, stream_type=stream_type)
                for field_name, value in file_info.items():
                    setattr(self, field_name, value)
        else:
            self.clear_fields()

    def full_clean(self, **kwargs):
        super(FileChangedMixin, self).full_clean(**kwargs)
        if self.file_changed and self.file.name:
            try:
                self.update_file_info()
            except GetFileInfoError:
                raise ValidationError("Can't get information about media file.")

    def save(self, *args, **kwargs):
        super(FileChangedMixin, self).save(*args, **kwargs)
        self._old_file = self.file


@python_2_unicode_compatible
class MediaFile(FileChangedMixin, MetaDataFields):
    """
    Base media file model.
    """
    title = models.CharField(_('title'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), unique=True,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    description = models.TextField(_('description'), blank=True)
    date_added = models.DateTimeField(_('date published'), default=now)

    def format_has_lower_quality(self, encode_format):
        raise NotImplementedError  # pragma: no cover

    def convert(self, encode_formats):
        """
        Converts media file to specified formats.
        If one of formats has higher quality than media file, then such format will be skipped.

        :param encode_formats: list of media file formats
        :type encode_formats: list
        :return: list with streams
        :rtype: list
        """
        encode_formats = list(filter(self.format_has_lower_quality, encode_formats))
        streams = []
        stream_cls = self.streams.model
        for encode_format in encode_formats:
            stream, created = stream_cls.objects.get_or_create(media_file=self, format=encode_format)
            stream.convert()
            streams.append(stream)
        return streams

    def update_streams(self):
        """
        Updates media file streams.

        :return: Returns list of updated steams.
        :rtype: list
        """
        logger.info('Update streams for: {}'.format(repr(self)))
        all_streams_formats = list(map(lambda s: s.format, self.streams.all()))
        if all_streams_formats:
            # Formats to be updated
            formats_to_be_updated = list(filter(self.format_has_lower_quality, all_streams_formats))
            logger.info('Update streams: {}'.format(formats_to_be_updated))

            # Formats with higher quality should be deleted
            formats_to_be_deleted = list(set(all_streams_formats) - set(formats_to_be_updated))
            logger.info('Delete streams: {}'.format(formats_to_be_deleted))
            for stream in self.streams.filter(format__in=formats_to_be_deleted).all():
                stream.cancel_conversion()
            self.streams.filter(format__in=formats_to_be_deleted).delete()
            return self.convert(formats_to_be_updated)
        return []

    def save(self, *args, **kwargs):
        """
        Updates streams if file has been changed.
        """
        file_changed = self.file_changed
        super(MediaFile, self).save(*args, **kwargs)
        if file_changed:
            self.update_streams()

    @property
    def content_type(self):
        if self.file.name:
            return mimetypes.guess_type(self.file.url)[0]

    def html_block(self):
        from avlogue.templatetags.avlogue_tags import avlogue_player
        context = avlogue_player(self)
        return render_to_string('avlogue/player_tag.html', context)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class Audio(MediaFile, AudioFields):
    """
    Uploaded audio.
    """
    objects = managers.AudioQuerySet.as_manager()

    file = models.FileField(_('audio file'), upload_to=settings.AUDIO_DIR, storage=settings.MEDIA_STORAGE,
                            validators=[audio_file_validator])

    def format_has_lower_quality(self, encode_format):
        """
        Return True if encode_format has a lower quality than current audio params.

        :param encode_format:
        :type encode_format: AudioFormat
        :rtype: bool
        :return:
        """
        bitrate = self.audio_bitrate or self.bitrate
        return bitrate >= (encode_format.audio_bitrate or 0)


class Video(MediaFile, VideoFields):
    """
    Uploaded video.
    """
    objects = managers.VideoQuerySet.as_manager()

    file = models.FileField(_('video file'), upload_to=settings.VIDEO_DIR, storage=settings.MEDIA_STORAGE,
                            validators=[video_file_validator])

    preview = models.FileField(_('video preview'), upload_to=settings.VIDEO_DIR, storage=settings.MEDIA_STORAGE,
                               null=True, blank=True)

    def admin_thumbnail(self):
        if self.preview:
            return '<img width="250" src="{}">'.format(self.preview.url)

    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def format_has_lower_quality(self, encode_format):
        """
        Return True if encode_format has a lower quality than current video params.

        :param encode_format:
        :type encode_format: VideoFormat
        :rtype: bool
        :return:
        """
        audio_bitrate = self.audio_bitrate or self.bitrate
        video_bitrate = self.video_bitrate or self.bitrate

        return audio_bitrate >= (encode_format.audio_bitrate or 0) \
            and video_bitrate >= (encode_format.video_bitrate or 0)

    def save(self, *args, **kwargs):
        file_changed = self.file_changed
        super(Video, self).save(*args, **kwargs)

        if file_changed or not self.preview.name:
            preview_changed = False
            if self.preview.name:
                self.preview.storage.delete(self.preview.name)
                self.preview = None
                preview_changed = True

            if self.file.name:
                filename = '{}.png'.format(os.path.splitext(os.path.basename(self.file.name))[0])
                temp_preview_file_path = os.path.join(settings.TEMP_PATH, filename)
                try:
                    default_encoder.get_file_preview(self.file.path, temp_preview_file_path)
                    self.preview = File(open(temp_preview_file_path, 'rb'))
                    preview_changed = True
                finally:
                    if os.path.exists(temp_preview_file_path):
                        os.remove(temp_preview_file_path)

            if preview_changed:
                self.save(update_fields=['preview'])


@python_2_unicode_compatible
class BaseStream(FileChangedMixin, MetaDataFields):
    CONVERSION_PREPARATION = 0
    CONVERSION_IN_PROGRESS = 1
    CONVERSION_SUCCESSFUL = 2
    CONVERSION_FAILURE = 3

    # Sort choices by status code to easy get text
    CONVERSION_CHOICES = sorted(((CONVERSION_PREPARATION, _('Preparation to conversion')),
                                 (CONVERSION_IN_PROGRESS, _('In progress')),
                                 (CONVERSION_SUCCESSFUL, _('Success')),
                                 (CONVERSION_FAILURE, _('Failure'))),
                                key=lambda s: s[0])

    created = models.DateTimeField(_('created'), auto_now=True)
    conversion_task_id = models.CharField(_('Conversion task id'), max_length=50, unique=True, null=True, blank=True)
    status = models.IntegerField(_('conversion status'), default=CONVERSION_PREPARATION, choices=CONVERSION_CHOICES)

    def get_status_text(self):
        return self.CONVERSION_CHOICES[self.status][1]

    def __str__(self):
        return "{}: {}".format(str(self.format), str(self.media_file))

    def clear_fields(self):
        """
        Clears stream before conversation.
        """
        super(BaseStream, self).clear_fields()
        self.conversion_task_id = None
        self.status = self.CONVERSION_PREPARATION
        self.file = None

    def cancel_conversion(self):
        if self.conversion_task_id is not None:
            AsyncResult(self.conversion_task_id).revoke()
            logger.info('Cancel conversion task: {}'.format(self.conversion_task_id))
        self.clear_fields()

    def convert(self):
        """
        Runs conversion task for the stream.
        :return: Celery AsyncResult.
        """
        logger.info('Start stream conversion: {}'.format(self))
        self.cancel_conversion()
        self.save()
        return tasks.encode_stream.delay(self.__class__, self.pk)

    @property
    def content_type(self):
        if self.file.name:
            return mimetypes.guess_type(self.file.url)[0]

    class Meta:
        abstract = True


class AudioStream(BaseStream, AudioFields):
    """
    Audio stream.
    """
    file = models.FileField(_('stream file'), upload_to=settings.AUDIO_STREAMS_DIR,
                            storage=settings.MEDIA_STREAMS_STORAGE)
    media_file = models.ForeignKey(Audio, on_delete=models.CASCADE, related_name='streams')
    format = models.ForeignKey(AudioFormat)

    class Meta:
        unique_together = ['media_file', 'format']


class VideoStream(BaseStream, VideoFields):
    """
    Video stream.
    """
    file = models.FileField(_('stream file'), upload_to=settings.VIDEO_STREAMS_DIR,
                            storage=settings.MEDIA_STREAMS_STORAGE)
    media_file = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='streams')
    format = models.ForeignKey(VideoFormat)

    class Meta:
        unique_together = ['media_file', 'format']


def delete_media_file_on_model_delete(sender, instance, **kwargs):
    """
    Deletes file if object was deleted.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.file.name:
        instance.file.storage.delete(instance.file.name)
    if isinstance(instance, Video) and instance.preview.name:
        instance.preview.storage.delete(instance.preview.name)


def delete_media_old_file_on_model_change(sender, instance, **kwargs):
    """
    Deletes old file if object file has been changed.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.file_changed and instance._old_file is not None and instance._old_file.name:
        instance._old_file.storage.delete(instance._old_file.name)


# Register media files deletion on model deletion
receiver(models.signals.post_delete, sender=Video)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=VideoStream)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=Audio)(delete_media_file_on_model_delete)
receiver(models.signals.post_delete, sender=AudioStream)(delete_media_file_on_model_delete)

# Register media files deletion on model changing
receiver(models.signals.pre_save, sender=Video)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=VideoStream)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=Audio)(delete_media_old_file_on_model_change)
receiver(models.signals.pre_save, sender=AudioStream)(delete_media_old_file_on_model_change)
