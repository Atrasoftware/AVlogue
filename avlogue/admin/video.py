from functools import partial

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avlogue.forms import BaseMediaFileModelForm
from avlogue.models import VideoStream, Video, VideoFormatSet
from avlogue.utils import media_file_convert_action


class VideoStreamInlineModelAdmin(admin.TabularInline):
    model = VideoStream
    extra = 0
    fields = ('format', 'file', 'video_codec', 'video_bitrate', 'resolution', 'bitrate', 'created', 'size')
    readonly_fields = fields

    def has_add_permission(self, request):
        return False


class VideoModelForm(BaseMediaFileModelForm):
    class Meta:
        model = Video
        fields = '__all__'


class VideoAdmin(admin.ModelAdmin):
    form = VideoModelForm
    list_display = ('title', 'file', 'date_added', 'resolution', 'video_codec', 'audio_codec', 'bitrate')
    readonly_fields = ('video_codec', 'video_bitrate', 'video_height', 'video_width',
                       'audio_codec', 'audio_bitrate', 'audio_channels',
                       'bitrate', 'size', 'duration', 'resolution')

    inlines = (VideoStreamInlineModelAdmin,)
    prepopulated_fields = {'slug': ('title',), }
    search_fields = ('title', 'slug')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'file', 'date_added')
        }),
        (_('Meta data'), {
            'fields': ('duration', 'bitrate', 'size')
        }),
        (_('Video stream'), {
            'fields': ('video_codec', 'video_bitrate', 'resolution'),
        }),
        (_('Audio stream'), {
            'fields': ('audio_codec', 'audio_bitrate', 'audio_channels'),
        }),
    )

    def get_actions(self, request):
        actions = super(VideoAdmin, self).get_actions(request)
        for format_set in VideoFormatSet.objects.all():
            action = partial(media_file_convert_action, format_set)
            name = 'convert_{}'.format(format_set.name)
            desc = _('Make/update streams for %(format_set)s format set.') % {'format_set': format_set.name}
            actions[name] = (action, name, desc)
        return actions
