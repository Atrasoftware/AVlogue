import os

import six
from django.core import files
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.text import slugify

from avlogue import utils
from avlogue.encoders import default_encoder


class BaseMediaFileQuerySet(models.QuerySet):
    """
    Base media file queryset.
    """

    def create_from_file(self, file, title=None, slug=None):
        """
        Creates video and fills fields with metadata.
        :param file: django.core.files.File or file path
        :param title:
        :param slug:
        :return:
        """
        stream_type = None
        from avlogue.models import Audio
        if issubclass(self.model, Audio):
            # Skips video stream info
            stream_type = 'audio'

        if isinstance(file, six.string_types):
            file = files.File(open(file, 'rb'))
        if isinstance(file, UploadedFile):
            file_info = utils.get_media_file_info_from_uploaded_file(file, stream_type=stream_type)
        else:
            file_info = default_encoder.get_file_info(file.name, stream_type=stream_type)

        if title is None:
            title = os.path.basename(file.name)[0:50]
        if slug is None:
            slug = slugify(title)

        return self.create(file=file, title=title, slug=slug, **file_info)


class VideoQuerySet(BaseMediaFileQuerySet):
    """
    Video queryset.
    """


class AudioQuerySet(BaseMediaFileQuerySet):
    """
    Audio queryset.
    """
