class BaseEncoder(object):
    """
    Base class for encoder.
    """

    @classmethod
    def get_file_info(cls, input_file):
        """
        Returns dict of VideoFile/AudioFile fields.
        :param input_file:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def encode(cls, media_file, output_file, encode_format):
        """
        Encodes media_file to specified encode_format.
        :param media_file:
        :param output_file:
        :param encode_format:
        :return:
        """
        raise NotImplementedError  # pragma: no cover
