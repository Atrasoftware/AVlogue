import os

import six

from django.core import files
from django.db import models
from django.utils.text import slugify

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
        file_info = default_encoder.get_file_info(file.name)
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
