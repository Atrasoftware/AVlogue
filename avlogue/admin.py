from django.contrib.admin import site
from avlogue.models import AudioFormat, VideoFormat, AudioFormatSet, \
    VideoFormatSet, AudioFile, VideoFile, AudioStream, VideoStream


site.register(AudioFormat)
site.register(VideoFormat)
site.register(AudioFormatSet)
site.register(VideoFormatSet)
site.register(AudioFile)
site.register(VideoFile)
site.register(AudioStream)
site.register(VideoStream)
