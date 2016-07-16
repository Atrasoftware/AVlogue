"""
Base encoder exceptions.
"""


class GetFileInfoError(Exception):
    """
    Exception, which can be raised during getting info about media file.
    """


class EncodeError(Exception):
    """
    Exception, which can be raised during encoding media file.
    """


class CreatePreviewError(Exception):
    """
    Exception, which can be raised during creating preview for media file.
    """
