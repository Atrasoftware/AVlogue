"""
AVlogue models test cases.
"""
import os

import mock
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from avlogue.encoders import default_encoder
from avlogue.models import Video, VideoFormat, AudioFormat, Audio, VideoFormatSet, AudioFormatSet, VideoStream, \
    video_file_validator, audio_file_validator
from avlogue.tests import factories
from avlogue.tests import mocks


class ModelsTestCase(TestCase):
    """
    AVlogue model tests.
    """

    fixtures = ['media-formats.json']

    def test_audio_video_formats(self):
        for media_format in (VideoFormat.objects.first(), AudioFormat.objects.first()):
            self.assertEqual(str(media_format), media_format.name)

        for media_format_set in (VideoFormatSet.objects.first(), AudioFormatSet.objects.first()):
            self.assertEqual(str(media_format_set), media_format_set.name)

    def test_video_resolution(self):
        """
        Tests video resolution format.
        """
        video = Video(video_height=1, video_width=2)
        self.assertEqual(video.resolution, '2x1')

        video = Video(video_height=None, video_width=2)
        self.assertEqual(video.resolution, '2x')

        video = Video(video_height=None, video_width=None)
        self.assertEqual(video.resolution, None)

    def test_null_content_type(self):
        """
        Tests content_type value if `file`field is None.
        """
        video = Video()
        self.assertIsNone(video.content_type)
        stream = VideoStream()
        self.assertIsNone(stream.content_type)

    def test_audio_video_file_crud(self):
        """
        Tests CRUD for Audio/Video.
        """

        def assert_media_file_fields(media_file):
            """
            Assert that Audio/Video object has the same fields as encoder provides.
            :param media_file:
            :return:
            """
            file_info = default_encoder.get_file_info(media_file.file.path)
            for key, val in file_info.items():
                self.assertEqual(getattr(media_file, key), val)

        def test_crud(media_format_cls, media_file_cls, file_factory):
            media_format = media_format_cls.objects.first()
            with file_factory(file_name='test_{}_file'.format(media_format.name),
                              encode_format=media_format) as file_path:
                # Test create by file path
                media_file = media_file_cls.objects.create_from_file(file_path, title='test media file')
                self.assertIsNotNone(media_file)
                self.assertEqual(str(media_file), 'test media file')
                self.assertIsNotNone(media_file.content_type)
                if issubclass(media_file_cls, Video):
                    self.assertIsNotNone(media_file.preview.name)
                    self.assertIsNotNone(media_file.admin_thumbnail())
                media_file.delete()

                # Test create by file object
                media_file = media_file_cls.objects.create_from_file(File(open(file_path, mode='rb')))
                self.assertIsNotNone(media_file)
                assert_media_file_fields(media_file)

                media_file.clear_fields()
                media_file.update_file_info()
                assert_media_file_fields(media_file)

                # Test create by uploaded in memory file object
                # file = open(file_path, mode='rb')
                file = InMemoryUploadedFile(open(file_path, mode='rb'), None, 'uploaded_file', 'text', 1, None)
                media_file = media_file_cls.objects.create_from_file(file)
                self.assertIsNotNone(media_file)
                assert_media_file_fields(media_file)

                # Check deletion of an old file during Audio/Video object changing
                with file_factory(file_name='new_test_media_file', encode_format=media_format) as new_file_path:
                    media_old_file_path = media_file.file.path
                    self.assertTrue(os.path.exists(media_old_file_path))

                    media_file.file = File(open(new_file_path, mode='rb'))
                    media_file.save()

                    self.assertFalse(os.path.exists(media_old_file_path))

                # Check Audio/Video file deletion during object deletion
                media_file_path = media_file.file.path
                if media_format_cls == Video:
                    preview_file_path = media_file.preview.path
                self.assertTrue(os.path.exists(media_file_path))
                media_file.delete()
                self.assertFalse(os.path.exists(media_file_path))
                if media_format_cls == Video:
                    self.assertFalse(os.path.exists(preview_file_path))

        test_crud(AudioFormat, Audio, factories.audio_file_factory)
        test_crud(VideoFormat, Video, factories.video_file_factory)

    def test_convert(self):
        """
        Test Audio/Video conversion and creation of streams.
        :return:
        """

        def test_media_file_conversion(media_file_cls):

            def mock_save(self, name, content):
                return name

            if issubclass(media_file_cls, Video):
                media_format_set = VideoFormatSet.objects.first()
            else:
                media_format_set = AudioFormatSet.objects.first()
            file_name = 'media_file.{}'.format(media_format_set.formats.first().container)

            def mock_path_exists(file_path):
                return True

            def mock_remove(file_path):
                return True

            with mock.patch.object(FileSystemStorage, 'save', mock_save):
                media_file = mocks.get_mock_media_file(file_name, media_file_cls)

                popen_patcher = mock.patch('subprocess.Popen')
                mock_popen = popen_patcher.start()
                mock_rv = mock.Mock()
                mock_rv.communicate.return_value = [None, None]
                mock_popen.return_value = mock_rv

                mock_file = mock.MagicMock(spec=mock.sentinel.file_spec)
                mock_file.size = 1
                mock_file.name = file_name
                mock_open = mock.MagicMock(return_value=mock_file)

                with mock.patch('avlogue.tasks.open', mock_open):
                    with mock.patch.object(default_encoder, 'get_file_info', mocks.get_file_info):
                        with mock.patch('os.path.exists', mock_path_exists):
                            with mock.patch('os.remove', mock_remove):
                                streams = media_file.convert(media_format_set.formats.all())

                                self.assertTrue(len(streams), media_format_set.formats.count() - 1)
                                for stream in streams:
                                    stream.refresh_from_db()

                                    self.assertEqual(str(stream), "{}: {}".format(str(stream.format), str(media_file)))
                                    self.assertEqual(stream.media_file.id, media_file.id)
                                    self.assertEqual(stream.status, stream.CONVERSION_SUCCESSFUL)
                                    self.assertEqual(stream.get_status_text(), 'Success')
                                    self.assertIsNotNone(stream.size)
                                    self.assertIsNotNone(stream.file.name)
                                    self.assertIsNone(stream.conversion_task_id)
                                    self.assertIsNotNone(stream.content_type,
                                                         'content type is None: {}'.format(stream))

                                updated_streams = media_file.update_streams()
                                self.assertEqual(list(s.id for s in updated_streams), list(s.id for s in streams))

                                stream = updated_streams[0]
                                stream.clear_fields()
                                self.assertEqual(stream.status, stream.CONVERSION_PREPARATION)
                                self.assertIsNone(stream.file.name)
                                self.assertIsNone(stream.conversion_task_id)
                                self.assertIsNone(stream.bitrate)

                self.assertIsNotNone(media_file.html_block())
                popen_patcher.stop()

        test_media_file_conversion(Audio)
        test_media_file_conversion(Video)

    def test_convert_to_higher_encode_format(self):
        """
        Tests that conversion will be not performed for the higher format.
        :return:
        """
        media_file = mocks.get_mock_media_file('media_file.mp3', Audio)
        format_with_higher_bitrate = AudioFormat(
            name='format_with_higher_bitrate',
            audio_bitrate=media_file.audio_bitrate + 1000,
            audio_codec=media_file.audio_codec
        )
        streams = media_file.convert((format_with_higher_bitrate,))
        self.assertEqual(len(streams), 0)
        self.assertEqual(media_file.streams.count(), 0)

    def test_conversion_failure(self):
        video = mocks.get_mock_media_file('media_file.mp3', Video, VideoFormat.objects.all())

        video_stream = video.streams.first()
        try:
            video_stream.convert()
        except Exception:
            pass

        video_stream.refresh_from_db()
        self.assertEqual(video_stream.status, video_stream.CONVERSION_FAILURE)

    def test_validators(self):
        video_file = mock.MagicMock()
        video_file.name = 'video.mp4'
        audio_file = mock.MagicMock()
        audio_file.name = 'audio.mp3'
        file = mock.MagicMock()
        file.name = 'document.pdf'

        audio_file_validator(audio_file)
        self.assertRaises(ValidationError, audio_file_validator, file)
        self.assertRaises(ValidationError, audio_file_validator, video_file)

        video_file_validator(video_file)
        self.assertRaises(ValidationError, video_file_validator, file)
        self.assertRaises(ValidationError, video_file_validator, audio_file)
