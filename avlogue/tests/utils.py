from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

from avlogue.mime import mimetypes


def get_in_memory_uploaded_file(file_path, content_type=None):
    """
    Returns InMemoryUploadedFile by file path.
    :param self:
    :param file_path:
    :param content_type:
    :return:
    """
    file_bytes = BytesIO()
    with open(file_path, 'rb') as input_file:
        file = File(input_file)
        for chunk in file.chunks():
            file_bytes.write(chunk)
    content_type = content_type or mimetypes.guess_type(file_path)[0]
    return InMemoryUploadedFile(file_bytes, 'file', file_path, content_type, file.size, None)
