"""
AVlogue forms tests.
"""
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import model_to_dict
from django.test import TestCase

from avlogue.admin.audio import AudioModelForm
from avlogue.models import AudioFormat, Audio, VideoFormat
from avlogue.tests import factories
from avlogue.tests import mocks
from avlogue.tests.utils import get_in_memory_uploaded_file


class ModelsTestCase(TestCase):
    fixtures = ['media-formats.json']

    def test_media_model_form_file_type(self):
        """
        Tests that form checks file type.
        :return:
        """
        audio_format = AudioFormat.objects.get(container='mp3')
        video_format = VideoFormat.objects.first()
        with factories.audio_file_factory('mock_audio', audio_format) as audio_file_path:
            audio = mocks.get_mock_media_file('mock_audio.mp3', Audio)
            audio_data = model_to_dict(audio)

            audio_form = AudioModelForm(audio_data,
                                        files={'file': get_in_memory_uploaded_file(audio_file_path)},
                                        instance=audio)
            self.assertTrue(audio_form.is_valid())

            with factories.video_file_factory('mock_video', video_format) as video_file_path:
                audio_form = AudioModelForm(audio_data,
                                            files={'file': get_in_memory_uploaded_file(video_file_path)},
                                            instance=audio)
                self.assertFalse(audio_form.is_valid())

                bytes = BytesIO()
                bytes.write(b'123')
                invalid_file_with_valid_content_type = InMemoryUploadedFile(bytes,
                                                                            'file',
                                                                            'invalid_file.mp3',
                                                                            'audio/mp3',
                                                                            1, None)
                audio_form = AudioModelForm(audio_data,
                                            files={'file': invalid_file_with_valid_content_type},
                                            instance=audio)
                self.assertFalse(audio_form.is_valid())
