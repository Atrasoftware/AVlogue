"""
FFMpegEncoder test cases.
"""
import os

import mock
from django.conf import settings
from django.test import TestCase
from unittest import skip

from avlogue.encoders import FFMpegEncoder
from avlogue.encoders.exceptions import EncodeError, GetFileInfoError, CreatePreviewError
from avlogue.models import Audio, AudioFormat, VideoFormat, Video
from avlogue.tests import factories
from avlogue.tests import mocks


class FFMpegEncoderTestCase(TestCase):
    """
    FFMpeg encoder test cases.
    """
    fixtures = ['media-formats.json']

    def test_get_file_info(self):
        """
        Tests FFMpegEncoder get_file_info.
        :return:
        """
        encoder = FFMpegEncoder()
        self.assertRaises(GetFileInfoError, encoder.get_file_info, 'invalid_file')
        with mock.patch.object(FFMpegEncoder, '_probe', lambda self, *args: mocks.ffprobe(*args)):
            encoder = FFMpegEncoder()
            info = encoder.get_file_info('video.mp4')
            self.assertEqual(info['video_codec'], mocks.MOCK_VIDEO_STREAM['codec_name'])
            self.assertEqual(info['video_bitrate'], int(mocks.MOCK_VIDEO_STREAM['bit_rate']))
            self.assertEqual(info['video_width'], mocks.MOCK_VIDEO_STREAM['width'])
            self.assertEqual(info['video_height'], mocks.MOCK_VIDEO_STREAM['height'])

            self.assertEqual(info['audio_codec'], mocks.MOCK_AUDIO_STREAM['codec_name'])
            self.assertEqual(info['audio_bitrate'], int(mocks.MOCK_AUDIO_STREAM['bit_rate']))
            self.assertEqual(info['audio_channels'], mocks.MOCK_AUDIO_STREAM['channels'])

            info = encoder.get_file_info('audio.mp3')
            self.assertEqual(info['audio_codec'], mocks.MOCK_AUDIO_STREAM['codec_name'])
            self.assertEqual(info['audio_bitrate'], int(mocks.MOCK_AUDIO_STREAM['bit_rate']))
            self.assertEqual(info['audio_channels'], mocks.MOCK_AUDIO_STREAM['channels'])

    def test_encode_with_invalid_params(self):
        """
        Tests FFMpegEncoder exceptions.
        :return:
        """

        def mock_file_save(self, name, content):
            return name

        encoder = FFMpegEncoder()
        self.assertRaises(TypeError, encoder.encode, 'media_file', '', '123')

        encode_format = AudioFormat.objects.first()
        media_file = mocks.get_mock_media_file('mock_audio.mp3', Audio)
        self.assertRaises(EncodeError, encoder.encode, media_file, '', encode_format)

    @skip("Checks encoding for all formats. Takes much time.")
    def test_encode(self):
        """
        Test encoding for default formats.
        """
        encoder = FFMpegEncoder()

        def test_encode_formats(encode_formats, media_file_cls):
            media_file_factory = None
            if media_file_cls == Audio:
                media_file_factory = factories.audio_file_factory
            elif media_file_cls == Video:
                media_file_factory = factories.video_file_factory

            for input_format in encode_formats:
                with media_file_factory('mock_media_{}'.format(str(input_format)), input_format) as input_file:
                    for encode_format in encode_formats:
                        if encode_format == input_format:
                            continue
                        media_file = media_file_cls.objects.create_from_file(input_file)
                        output_file = os.path.join(settings.MEDIA_ROOT,
                                                   'mock_encoded_media_.{}'.format(input_format.name,
                                                                                   input_format.container))
                        try:
                            encoder.encode(media_file, output_file, encode_format)
                            self.assertTrue(os.path.exists(output_file))
                            output_file_info = encoder.get_file_info(output_file)
                            if media_file_cls in (Audio, Video):
                                self.assertEqual(output_file_info['audio_codec'], encode_format.audio_codec)

                            if media_file_cls == Video:
                                self.assertEqual(output_file_info['video_codec'], encode_format.video_codec)

                        finally:
                            media_file.delete()
                            os.remove(output_file)

        test_encode_formats(VideoFormat.objects.all(), Video)
        test_encode_formats(AudioFormat.objects.all(), Audio)

    def test_get_file_preview(self):
        encoder = FFMpegEncoder()
        input_format = VideoFormat.objects.first()
        with factories.audio_file_factory('mock_audio', input_format) as input_file:
            self.assertRaises(CreatePreviewError, encoder.get_file_preview, input_file, 'output')
