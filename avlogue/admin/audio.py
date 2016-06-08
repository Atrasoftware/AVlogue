from functools import partial

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avlogue.forms import BaseMediaFileModelForm
from avlogue.models import AudioStream, Audio, AudioFormatSet
from avlogue.utils import media_file_convert_action


class AudioStreamInlineModelAdmin(admin.TabularInline):
    model = AudioStream
    extra = 0
    fields = ('format', 'file', 'audio_codec', 'audio_bitrate', 'bitrate', 'audio_channels', 'created', 'size')
    readonly_fields = fields

    def has_add_permission(self, request):
        return False


class AudioModelForm(BaseMediaFileModelForm):
    class Meta:
        model = Audio
        fields = '__all__'


class AudioAdmin(admin.ModelAdmin):
    form = AudioModelForm
    list_display = ('title', 'file', 'date_added', 'audio_codec', 'bitrate')
    readonly_fields = ('audio_codec', 'audio_bitrate', 'audio_channels',
                       'bitrate', 'size', 'duration')
    inlines = (AudioStreamInlineModelAdmin,)
    prepopulated_fields = {'slug': ('title',), }
    search_fields = ('title', 'slug')

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

    def get_actions(self, request):
        actions = super(AudioAdmin, self).get_actions(request)
        for format_set in AudioFormatSet.objects.all():
            action = partial(media_file_convert_action, format_set)
            name = 'convert_{}'.format(format_set.name)
            desc = _('Make/update streams for %(format_set)s format set.') % {'format_set': format_set.name}
            actions[name] = (action, name, desc)
        return actions
