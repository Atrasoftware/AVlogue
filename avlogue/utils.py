import re

from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from avlogue.mime import mimetypes
from avlogue import settings
from avlogue.encoders import default_encoder


@deconstructible
class ContentTypeValidator(object):
    """
    Validates file content type.
    """
    message = _("File has invalid type.")
    code = 'invalid_content_type'

    def __init__(self, allowed_content_types, message=None, code=None):
        """
        :param allowed_content_types: list of content type regular expressions
        :param message:
        :param code:
        """
        self.allowed_content_types = []
        for content_type in allowed_content_types:
            self.allowed_content_types.append(re.compile(content_type))

        self.message = message or self.message
        self.code = code or self.code

    def __call__(self, file_field):
        file_content_type = mimetypes.guess_type(file_field.file.name)[0] or ''
        for content_type in self.allowed_content_types:
            if content_type.match(file_content_type):
                return
        raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.allowed_content_types == other.allowed_content_types and
            self.message == other.message and
            self.code == other.code
        )


def get_media_file_info_from_uploaded_file(file, encoder=None):
    """
    Saves file in memory into temporary path and returns info about it.
    :param file: django.core.files.File instance
    :param encoder: BaseEncoder instance or None
    :return:
    """
    encoder = encoder or default_encoder
    if isinstance(file, TemporaryUploadedFile):
        return encoder.get_file_info(file.file.name)
    elif isinstance(file, InMemoryUploadedFile):
        with NamedTemporaryFile(delete=True, dir=settings.TEMP_PATH) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            return encoder.get_file_info(temp_file.name)
    else:
        raise TypeError('file must be instance of TemporaryUploadedFile or InMemoryUploadedFile')


def media_file_convert_action(format_set, model_admin, request, queryset):
    """
    Model admin abstract action for making streams.
    :param format_set:
    :param model_admin:
    :param request:
    :param queryset:
    :return:
    """
    format_set_cls = format_set._meta.model
    try:
        format_set = format_set_cls.objects.get(pk=format_set.pk)
    except format_set_cls.DoesNotExist:
        model_admin.message_user(request, _("Format set does'nt exist."))
    else:
        for obj in queryset:
            obj.convert(format_set.formats.all())
        model_admin.message_user(request, _("Streams creating is in process. They will be available soon."))
