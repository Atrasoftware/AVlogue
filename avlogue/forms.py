from django import forms
from django.utils.translation import ugettext_lazy as _

from avlogue import utils
from avlogue.encoders.exceptions import GetFileInfoError


class BaseMediaFileModelForm(forms.ModelForm):
    """
    Base media file model form.
    """

    def full_clean(self):
        """
        Gets information about uploaded media file and set it to the instance.
        :return:
        """
        super(BaseMediaFileModelForm, self).full_clean()
        if self.is_valid() and 'file' in self.changed_data:
            try:
                file_info = utils.get_media_file_info_from_file_in_memory(self.cleaned_data['file'])
            except GetFileInfoError:
                self.add_error('file', _("Can't get information about media file."))
            else:
                for key, val in file_info.items():
                    setattr(self.instance, key, val)
