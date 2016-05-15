import six

from django.core import files
from django.db import models

from avlogue.encoders import default_encoder


class BaseMediaFileQuerySet(models.QuerySet):
    """
    Base media file queryset.
    """

    def create_from_file(self, file):
        """
        Creates video file and fills fields with metadata.
        :param file: django.core.files.File or file path
        :return:
        """
        if isinstance(file, six.string_types):
            file = files.File(open(file, 'rb'))
        file_info = default_encoder.get_file_info(file.name)
        return self.create(file=file, **file_info)


class VideoFileQuerySet(BaseMediaFileQuerySet):
    """
    Video file queryset.
    """


class AudioFileQuerySet(BaseMediaFileQuerySet):
    """
    Audio file queryset.
    """
