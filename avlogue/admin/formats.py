from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class VideoFormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'video_codec', 'video_bitrate', 'resolution', 'container')
    list_filter = ('video_codec', 'container')

    fieldsets = (
        (None, {
            'fields': ('name', 'container')
        }),
        (_('Video stream'), {
            'fields': ('video_codec', 'video_bitrate', 'video_width', 'video_height',
                       'video_aspect_mode', 'video_codec_params'),
        }),
        (_('Audio stream'), {
            'fields': ('audio_codec', 'audio_bitrate', 'audio_channels', 'audio_codec_params'),
        }),
    )


class VideoFormatSetAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AudioFormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'audio_codec', 'audio_bitrate', 'container')
    list_filter = ('audio_codec', 'container')

    fieldsets = (
        (None, {
            'fields': ('name', 'container')
        }),
        (_('Audio stream'), {
            'fields': ('audio_codec', 'audio_bitrate', 'audio_channels', 'audio_codec_params'),
        }),
    )


class AudioFormatSetAdmin(admin.ModelAdmin):
    list_display = ('name',)
