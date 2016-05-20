from django.contrib import admin

from avlogue.admin.audio import AudioAdmin
from avlogue.admin.formats import AudioFormatAdmin, VideoFormatAdmin, AudioFormatSetAdmin, VideoFormatSetAdmin
from avlogue.admin.video import VideoAdmin
from avlogue.models import AudioFormat, VideoFormat, AudioFormatSet, VideoFormatSet, Audio, Video

admin.site.register(AudioFormat, AudioFormatAdmin)
admin.site.register(VideoFormat, VideoFormatAdmin)
admin.site.register(AudioFormatSet, AudioFormatSetAdmin)
admin.site.register(VideoFormatSet, VideoFormatSetAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(Video, VideoAdmin)
