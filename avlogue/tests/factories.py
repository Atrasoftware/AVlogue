"""
Audio/Video factories to be used during testing.
"""
import os
import subprocess
from contextlib import contextmanager

from avlogue import settings
from avlogue.encoders import FFMpegEncoder


@contextmanager
def video_file_factory(file_name, encode_format, duration=10, output_dir=None):
    """
    Context manager to create mock video file by encode_format.
    Video file will be deleted after exiting from statement.
    :param file_name:
    :param encode_format:
    :param duration:
    :param output_dir:
    :return: mock file path
    """
    output_dir = output_dir or os.path.dirname(__file__)
    output_file = os.path.join(output_dir, '{}.{}'.format(file_name, encode_format.container))
    encoder = FFMpegEncoder()
    audio_params = encoder._get_audio_params(encode_format)
    video_params = encoder._get_video_params(encode_format)
    cmd = [settings.FFMPEG_EXECUTABLE, '-y', '-loglevel', 'error',
           '-ar', '48000', '-f', 's16le', '-i', '/dev/zero',
           '-f', 'lavfi', '-i', 'smptebars']
    cmd.extend(video_params)
    cmd.extend(audio_params)
    cmd.extend(('-t', str(duration), output_file))
    cmd.extend(('-f', encode_format.container))

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        errors = p.communicate()[1]
        if errors:
            raise Exception(errors)
        yield output_file
    except Exception as e:
        # Don't remove file if assertion error
        if not isinstance(e, AssertionError):
            if os.path.exists(output_file):
                os.remove(output_file)
        raise e

    if os.path.exists(output_file):
        os.remove(output_file)


@contextmanager
def audio_file_factory(file_name, encode_format, duration=10, output_dir=None):
    """
    Context manager to create mock audio file by encode_format.
    Audio file will be deleted after exiting from statement.
    :param file_name:
    :param encode_format:
    :param duration:
    :return: mock file path
    """
    output_dir = output_dir or os.path.dirname(__file__)
    output_file = os.path.join(output_dir, '{}.{}'.format(file_name, encode_format.container))
    encoder = FFMpegEncoder()
    audio_params = encoder._get_audio_params(encode_format)
    cmd = [settings.FFMPEG_EXECUTABLE, '-y', '-loglevel', 'error',
           '-ar', '48000', '-f', 's16le', '-i', '/dev/zero']
    cmd.extend(audio_params)
    cmd.extend(('-t', str(duration), output_file))
    cmd.extend(('-f', encode_format.container))

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        errors = p.communicate()[1]
        if errors:
            raise Exception(errors)
        yield output_file
    except Exception as e:
        # Don't remove file if assertion error
        if not isinstance(e, AssertionError):
            if os.path.exists(output_file):
                os.remove(output_file)
        raise e

    if os.path.exists(output_file):
        os.remove(output_file)
