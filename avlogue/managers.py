import os

import six
from django.core import files
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
        if isinstance(file, six.string_types):
            file = files.File(open(file, 'rb'))

        stream_type = None
        from avlogue.models import Audio
        if issubclass(self.model, Audio):
            # Skips video stream info
            stream_type = 'audio'

        with utils.get_local_file_path(file) as file_path:
            file_info = default_encoder.get_file_info(file_path, stream_type=stream_type)

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
