from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avlogue.admin.base import BaseStreamForm, BaseMediaFileAdminMixin
from avlogue.forms import BaseMediaFileModelForm
from avlogue.models import VideoStream, Video


class VideoStreamModelForm(BaseStreamForm):
    class Meta:
        model = VideoStream
        fields = '__all__'


class VideoStreamInlineModelAdmin(admin.TabularInline):
    model = VideoStream
    form = VideoStreamModelForm

    extra = 0
    fields = ('file', 'status', 'resolution', 'bitrate', 'size', 'created', 'update',)
    readonly_fields = tuple(set(fields) - set(('update',)))

    def has_add_permission(self, request):
        return False


class VideoModelForm(BaseMediaFileModelForm):
    class Meta:
        model = Video
        fields = '__all__'


class VideoAdmin(BaseMediaFileAdminMixin, admin.ModelAdmin):
    form = VideoModelForm
    list_display = ('admin_thumbnail', 'title', 'file', 'date_added', 'resolution', 'video_codec', 'audio_codec',
                    'bitrate')
    readonly_fields = ('video_codec', 'video_bitrate', 'video_height', 'video_width',
                       'audio_codec', 'audio_bitrate', 'audio_channels',
                       'bitrate', 'size', 'duration', 'resolution')
    list_display_links = ('admin_thumbnail', 'title',)
    inlines = (VideoStreamInlineModelAdmin,)
    prepopulated_fields = {'slug': ('title',)}
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
