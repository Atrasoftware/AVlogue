from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avlogue.admin.base import BaseStreamForm, BaseMediaFileAdminMixin
from avlogue.models import AudioStream, AudioFormatSet


class AudioStreamModelForm(BaseStreamForm):
    class Meta:
        model = AudioStream
        fields = '__all__'


class AudioStreamInlineModelAdmin(admin.TabularInline):
    model = AudioStream
    form = AudioStreamModelForm
    extra = 0
    fields = ('file', 'status', 'bitrate', 'size', 'created', 'update',)
    readonly_fields = tuple(set(fields) - set(('update',)))

    def has_add_permission(self, request):
        return False


class AudioAdmin(BaseMediaFileAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'file', 'date_added', 'audio_codec', 'bitrate')
    readonly_fields = ('audio_codec', 'audio_bitrate', 'audio_channels',
                       'bitrate', 'size', 'duration')
    inlines = (AudioStreamInlineModelAdmin,)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'slug')
    format_set_class = AudioFormatSet
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'file', 'date_added')
        }),
        (_('Meta data'), {
            'fields': ('duration', 'bitrate', 'size')
        }),
        (_('Audio stream'), {
            'fields': ('audio_codec', 'audio_bitrate', 'audio_channels'),
        }),
    )
