"""
AVlogue template tags test cases.
"""

from django.test import TestCase

from avlogue.models import AudioFormat, Audio, AudioFormatSet
from avlogue.templatetags.avlogue_tags import avlogue_player
from avlogue.tests import mocks


class TemplateTagsTestCase(TestCase):
    fixtures = ['media-formats.json']

    def test_player_tag(self):
        """
        Tests avlogue player template tag context.
        """

        audio_format_set = AudioFormatSet.objects.first()
        media_file = mocks.get_mock_media_file('media_file.mp3', Audio, audio_format_set.formats.all())
        format1, format2 = AudioFormat.objects.all()[0:2]

        context = avlogue_player(media_file, formats=','.join((format1.name, format2.name)))
        self.assertEqual(len(context['streams']), 2)
        self.assertEqual(len(context['streams'].filter(id__in=(format1.id, format2.id))), 2)

        context = avlogue_player(media_file, formats=','.join((format1.name, format2.name)),
                                 bitrate=format2.audio_bitrate)
        self.assertEqual(len(context['streams']), 1)
        self.assertEqual(context['streams'][0].format, format2)

        context = avlogue_player(media_file, formats=','.join((format1.name, format2.name)),
                                 max_bitrate=format2.audio_bitrate, min_bitrate=format2.audio_bitrate)
        self.assertEqual(len(context['streams']), 1)
        self.assertEqual(context['streams'][0].format, format2)

        context = avlogue_player(media_file, format_sets=audio_format_set.name)
        self.assertEqual(list(s.format.id for s in context['streams']),
                         list(f.id for f in audio_format_set.formats.all()))
        self.assertRaises(TypeError, avlogue_player, 'Invalid type')
