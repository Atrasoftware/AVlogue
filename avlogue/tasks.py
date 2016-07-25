"""
AVlogue celery tasks to convert audio/video.
"""
import logging
import os

from celery import shared_task
from django.core import files
from django.utils.text import slugify

from avlogue import settings
from avlogue.encoders import default_encoder


@shared_task(bind=True)
def encode_stream(self, stream_cls, stream_pk):
    logger = logging.getLogger('avlogue')
    stream = stream_cls.objects.filter(pk=stream_pk).first()

    if stream is None:
        logger.warning("{} stream object was not found by pk={}".format(stream_cls.__name__, stream_pk))
    else:
        from avlogue.models import AudioStream
        if issubclass(stream_cls, AudioStream):
            # Skips video stream info
            stream_type = 'audio'
        else:
            stream_type = None

        stream.conversion_task_id = self.request.id
        stream.status = stream.CONVERSION_IN_PROGRESS
        stream.save()

        output_filename = os.path.splitext(os.path.basename(stream.media_file.file.name))[0]
        output_filename = '{}_{}.{}'.format(output_filename, slugify(stream.format.name), stream.format.container)
        output_file = os.path.join(settings.TEMP_PATH, output_filename)

        try:
            default_encoder.encode(stream.media_file, output_file, stream.format)

            stream.file = files.File(open(output_file, 'rb'))
            stream_file_info = default_encoder.get_file_info(output_file, stream_type)
            for field_name, value in stream_file_info.items():
                setattr(stream, field_name, value)
            stream.status = stream.CONVERSION_SUCCESSFUL
            stream.conversion_task_id = None
            stream.save()
        except Exception as e:
            logger.error('Conversion of {} failed.\nException:\n{}'.format(repr(stream), str(e)))
            stream.status = stream.CONVERSION_FAILURE
            stream.save()
            raise e
        finally:
            # remove temporary file
            if output_file is not None and os.path.exists(output_file):
                os.remove(output_file)
