"""
AVlogue celery tasks to convert audio/video.
"""
import logging
import os

from celery import shared_task
from django.conf import settings as django_settings
from django.core import files

from avlogue import settings
from avlogue.encoders import default_encoder


@shared_task
def encode_media_file(media_file, encoded_formats):
    streams = []
    for encode_format in encoded_formats:
        output_filename = os.path.splitext(os.path.basename(media_file.file.name))[0]
        output_filename = '{}_{}.{}'.format(output_filename, encode_format.name, encode_format.container)
        output_file = os.path.join(settings.TEMP_PATH, output_filename)

        try:
            default_encoder.encode(media_file, output_file, encode_format)
        except Exception as e:
            logger = logging.getLogger('django')
            logger.error('Conversion to {} failed.\nException:\n{}'.format(repr(encode_format), str(e)))
            if django_settings.DEBUG:  # pragma: no cover
                raise e
        else:
            stream_file = files.File(open(output_file, 'rb'))
            stream_cls = media_file.streams.model

            try:
                stream = stream_cls.objects.get(media_file=media_file, format=encode_format)
            except stream_cls.DoesNotExist:
                stream = stream_cls(media_file=media_file, format=encode_format)
            stream.file = stream_file
            stream_file_info = default_encoder.get_file_info(output_file)
            for field_name, value in stream_file_info.items():
                setattr(stream, field_name, value)
            stream.save()

            streams.append(stream)
        finally:
            # remove temporary file
            if os.path.exists(output_file):
                os.remove(output_file)

    return streams
