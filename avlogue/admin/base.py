from functools import partial

from django import forms
from django.utils.translation import ugettext_lazy as _

from avlogue.models import VideoFormatSet, Video, AudioFormatSet
from avlogue.utils import media_file_convert_action


class BaseStreamForm(forms.ModelForm):
    update = forms.BooleanField(label=_('Update'), required=False)


class BaseMediaFileAdminMixin(object):
    def save_formset(self, request, form, formset, change):
        """
        Runs encoding of the selected streams.
        """
        for stream_form in formset:
            if stream_form.cleaned_data.get('update'):
                stream_form.instance.convert()
        super(BaseMediaFileAdminMixin, self).save_formset(request, form, formset, change)

    def get_actions(self, request):
        """
        Adds actions to create streams by format sets.
        """
        actions = super(BaseMediaFileAdminMixin, self).get_actions(request)
        format_set_class = VideoFormatSet if issubclass(self.model, Video) else AudioFormatSet
        for format_set in format_set_class.objects.all():
            action = partial(media_file_convert_action, format_set)
            name = 'convert_{}'.format(format_set.name)
            desc = _('Make/update streams for %(format_set)s format set.') % {'format_set': format_set.name}
            actions[name] = (action, name, desc)
        return actions
