class BaseEncoder(object):
    """
    Base class for encoder.
    """

    def get_file_info(self, input_file):
        """
        Returns information about media file.

        :param input_file: input file path
        :type input_file: str
        :return: Dictionary populated with Audio or Video fields
        :rtype: dict
        """
        raise NotImplementedError  # pragma: no cover

    def encode(self, media_file, output_file, encode_format):
        """
        Encodes media_file to specified encode_format.

        :param media_file:
        :type media_file: avlogue.models.MediaFile
        :param output_file: output file path
        :type output_file: str
        :param encode_format:
        :type encode_format: avlogue.models.BaseFormat
        """
        raise NotImplementedError  # pragma: no cover

    def get_file_preview(self, input_file, output_file):
        """
        Returns preview for media file.

        :param input_file:
        :type input_file: str
        :param output_file:
        :type output_file: str
        """
        raise NotImplementedError  # pragma: no cover
