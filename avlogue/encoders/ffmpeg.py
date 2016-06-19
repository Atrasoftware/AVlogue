import json
import logging
import subprocess

from avlogue import settings
from avlogue.encoders.base import BaseEncoder
from avlogue.encoders.exceptions import GetFileInfoError, EncodeError

logger = logging.getLogger('django')


class FFProbeError(GetFileInfoError):
    """
    ffprobe command execution error.
    """
    pass


class FFMpegEncoderError(EncodeError):
    """
    ffmpeg command execution error.
    """
    pass


class FFMpegEncoder(BaseEncoder):
    """
    FFMpeg encoder.
    """

    def _probe(self, input_file):
        """
        Executes ffprobe to get streams info.
        :param input_file:
        :return:
        """
        cmd = (settings.FFPROBE_EXECUTABLE, input_file, '-loglevel', 'error',
               '-show_streams', '-show_format', '-print_format', 'json')

        logger.debug('ffprobe command: {}'.format(cmd))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        if errors:
            logger.error('ffprobe error: {}.\ncmd={}'.format(errors, cmd))
            raise FFProbeError(errors, cmd)
        if isinstance(output, bytes):
            output = output.decode('utf-8')
        return json.loads(output)

    def _parse_audio_stream_data(self, stream):
        bit_rate = stream.get('bit_rate')  # NOTE: ffprobe may not return bitrate
        if bit_rate is not None:
            bit_rate = int(bit_rate)
        codec = stream['codec_name']
        return {
            'audio_codec': codec,
            'audio_bitrate': bit_rate,
            'audio_channels': int(stream['channels'])
        }

    def _parse_video_stream_data(self, stream):
        bit_rate = stream.get('bit_rate')  # NOTE: ffprobe may not return bitrate
        if bit_rate is not None:
            bit_rate = int(bit_rate)
        codec = stream['codec_name']
        return {
            'video_codec': codec,
            'video_bitrate': bit_rate,
            'video_width': int(stream['width']),
            'video_height': int(stream['height'])
        }

    def get_file_info(self, input_file):
        """
        Executes ffprobe to get information about media file.

        :param input_file: input file path
        :type input_file: str

        :return: Dictionary populated with Audio or Video fields
        :rtype: dict
        """
        probe_data = self._probe(input_file)

        # NOTE: first streams are used
        video_streams = filter(lambda s: s['codec_type'] == 'video', probe_data['streams'])
        audio_streams = filter(lambda s: s['codec_type'] == 'audio', probe_data['streams'])

        if isinstance(video_streams, list):
            video_streams = iter(video_streams)
        if isinstance(audio_streams, list):
            audio_streams = iter(audio_streams)
        video_stream = next(video_streams, None)
        audio_stream = next(audio_streams, None)

        info = {
            'bitrate': int(probe_data['format']['bit_rate']),
            'size': int(probe_data['format']['size']),
            'duration': float(probe_data['format']['duration'])
        }
        if video_stream is not None:
            info.update(self._parse_video_stream_data(video_stream))
        if audio_stream is not None:
            info.update(self._parse_audio_stream_data(audio_stream))

        return info

    def _get_audio_params(self, encode_format):
        params = []
        audio_codec = settings.AUDIO_CODECS[encode_format.audio_codec]
        if audio_codec is not None:
            params.extend(('-acodec', audio_codec))
        if encode_format.audio_bitrate is not None:
            params.extend(('-b:a', str(encode_format.audio_bitrate)))

        if encode_format.audio_codec_params:
            params.extend(encode_format.audio_codec_params.split(' '))

        if encode_format.audio_channels is not None:
            params.extend(('-ac', str(encode_format.audio_channels)))

        return params

    def _get_video_params(self, encode_format):
        params = ['-vcodec', settings.VIDEO_CODECS[encode_format.video_codec]]
        if encode_format.video_codec_params:
            params.extend(encode_format.video_codec_params.split(' '))

        if encode_format.video_bitrate is not None:
            params.extend(('-b:v', str(encode_format.video_bitrate)))
            params.extend(('-maxrate', str(encode_format.video_bitrate)))
            params.extend(('-bufsize', str(encode_format.video_bitrate * 2)))

        if encode_format.video_width is not None or encode_format.video_height is not None:
            video_width = encode_format.video_width or '-2'
            video_height = encode_format.video_height or '-2'
            if encode_format.video_aspect_mode == 'scale':
                params.extend(('-vf', 'scale={}:{}'.format(video_width, video_height)))
            elif encode_format.video_aspect_mode == 'scale_crop':
                params.extend(('-vf', 'scale=(iw * sar) * max({width} / (iw * sar)\, {height}/ ih)'
                                      ':ih * max({width} / (iw * sar)\, {height} / ih), crop={width}:{height}'
                               .format(width=video_width, height=video_height)))
        return params

    def encode(self, media_file, output_file, encode_format):
        """
        Encode media_file to the encode_format with ffmpeg.

        :param media_file: Video or Audio
        :type media_file: avlogue.models.MediaFile
        :param output_file: output file path
        :type output_file: str
        :param encode_format: VideoFormat or AudioFormat
        :type encode_format: avlogue.models.BaseFormat

        :rtype: subprocess.Popen
        """
        from avlogue.models import Video, Audio

        if not isinstance(media_file, (Video, Audio)):
            raise TypeError('media_file must be instance of Video or Audio')

        cmd = [settings.FFMPEG_EXECUTABLE, '-y', '-i', media_file.file.path]
        cmd.extend(('-loglevel', 'error'))
        if isinstance(media_file, Video):
            containers = settings.VIDEO_CONTAINERS
            cmd.extend(self._get_video_params(encode_format))
            cmd.extend(('-threads', '0'))
            cmd.extend(self._get_audio_params(encode_format))

        elif isinstance(media_file, Audio):
            containers = settings.AUDIO_CONTAINERS
            cmd.extend(self._get_audio_params(encode_format))

        cmd.extend(('-f', containers[encode_format.container]))
        cmd.append(output_file)

        logger.debug('ffmpeg encode command: {}'.format(cmd))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        errors = p.communicate()[1]
        if errors:
            logger.error('ffmpeg conversion error: {}.Encode format: {}.\nFile: {}.\nCommand: {}.'.format(
                errors, repr(encode_format), repr(media_file), cmd))
            raise FFMpegEncoderError(errors, cmd)
        return p
