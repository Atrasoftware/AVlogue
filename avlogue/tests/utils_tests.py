"""
AVlogue utils test cases.
"""

from django.core.files import File
from django.test import TestCase

from avlogue import utils
from avlogue.encoders import default_encoder
from avlogue.models import AudioFormat
from avlogue.tests import factories
from avlogue.tests.utils import get_in_memory_uploaded_file


class UtilsTestCase(TestCase):
    fixtures = ['media-formats.json']

    def test_get_media_file_info_from_uploaded_file(self):
        """
        Tests getting information about uploaded media file.
        """
        audio_format = AudioFormat.objects.first()
        with factories.audio_file_factory('mock_audio', audio_format) as file_path:
            with open(file_path, 'rb') as input_file:
                file = File(input_file)
                self.assertRaises(TypeError, utils.get_media_file_info_from_uploaded_file, file)

            uploaded_file = get_in_memory_uploaded_file(file_path)
            self.assertEqual(
                default_encoder.get_file_info(file_path),
                utils.get_media_file_info_from_uploaded_file(uploaded_file)
            )
