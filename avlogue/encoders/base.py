class BaseEncoder(object):
    """
    Base class for encoder.
    """

    def get_file_info(self, input_file):
        """
        Returns dict of Video/Audio fields.
        :param input_file:
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    def encode(self, media_file, output_file, encode_format):
        """
        Encodes media_file to specified encode_format.
        :param media_file:
        :param output_file:
        :param encode_format:
        :return:
        """
        raise NotImplementedError  # pragma: no cover
