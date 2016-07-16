import os
import random

import mock
from django.core.files.storage import File, FileSystemStorage

from avlogue import settings
from avlogue.encoders import default_encoder
from avlogue.models import Audio, Video

MOCK_VIDEO_STREAM = {
    "index": 0,
    "codec_name": "h264",
    "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
    "profile": "Main",
    "codec_type": "video",
    "codec_time_base": "1/50",
    "codec_tag_string": "avc1",
    "codec_tag": "0x31637661",
    "width": 1280,
    "height": 720,
    "coded_width": 1280,
    "coded_height": 720,
    "has_b_frames": 0,
    "sample_aspect_ratio": "1:1",
    "display_aspect_ratio": "16:9",
    "pix_fmt": "yuv420p",
    "level": 31,
    "chroma_location": "left",
    "refs": 1,
    "is_avc": "true",
    "nal_length_size": "4",
    "r_frame_rate": "25/1",
    "avg_frame_rate": "25/1",
    "time_base": "1/12800",
    "start_pts": 0,
    "start_time": "0.000000",
    "duration_ts": 67584,
    "duration": "5.280000",
    "bit_rate": "1205959",
    "bits_per_raw_sample": "8",
    "nb_frames": "132",
    "disposition": {
        "default": 1,
        "dub": 0,
        "original": 0,
        "comment": 0,
        "lyrics": 0,
        "karaoke": 0,
        "forced": 0,
        "hearing_impaired": 0,
        "visual_impaired": 0,
        "clean_effects": 0,
        "attached_pic": 0
    },
    "tags": {
        "creation_time": "1970-01-01 00:00:00",
        "language": "und",
        "handler_name": "VideoHandler"
    }
}
MOCK_AUDIO_STREAM = {
    "index": 1,
    "codec_name": "aac",
    "codec_long_name": "AAC (Advanced Audio Coding)",
    "profile": "LC",
    "codec_type": "audio",
    "codec_time_base": "1/48000",
    "codec_tag_string": "mp4a",
    "codec_tag": "0x6134706d",
    "sample_fmt": "fltp",
    "sample_rate": "48000",
    "channels": 6,
    "channel_layout": "5.1",
    "bits_per_sample": 0,
    "r_frame_rate": "0/0",
    "avg_frame_rate": "0/0",
    "time_base": "1/48000",
    "start_pts": 0,
    "start_time": "0.000000",
    "duration_ts": 254976,
    "duration": "5.312000",
    "bit_rate": "384828",
    "max_bit_rate": "400392",
    "nb_frames": "249",
    "disposition": {
        "default": 1,
        "dub": 0,
        "original": 0,
        "comment": 0,
        "lyrics": 0,
        "karaoke": 0,
        "forced": 0,
        "hearing_impaired": 0,
        "visual_impaired": 0,
        "clean_effects": 0,
        "attached_pic": 0
    },
    "tags": {
        "creation_time": "1970-01-01 00:00:00",
        "language": "und",
        "handler_name": "SoundHandler"
    }
}

MOCK_FORMAT = {
    "filename": "",
    "nb_streams": 1,
    "nb_programs": 0,
    "format_name": "",
    "format_long_name": "",
    "start_time": "0.000000",
    "duration": "10.016000",
    "size": "160256",
    "bit_rate": "128000",
    "probe_score": 51
}


def ffprobe(input_file):
    """
    Returns mock ffprobe output by input_file.
    :param input_file:
    :return:
    """
    ext = os.path.splitext(os.path.basename(input_file))[1][1:].lower()

    format_data = MOCK_FORMAT.copy()
    format_data['filename'] = input_file
    format_data['format_name'] = ext
    format_data['format_long_name'] = 'Test mock {} format'.format(ext)

    if ext in settings.AUDIO_CONTAINERS:
        format_data['streams'] = 1
        return {"streams": [MOCK_AUDIO_STREAM], 'format': format_data}
    elif ext in settings.VIDEO_CONTAINERS:
        format_data['streams'] = 2
        return {"streams": [MOCK_VIDEO_STREAM, MOCK_AUDIO_STREAM], 'format': format_data}
    else:
        raise Exception('Unknown input file format: {}'.format(input_file))


def get_file_info(input_file):
    """
    Returns mock streams info by input_file.
    :param input_file:
    :return:
    """
    ext = os.path.splitext(os.path.basename(input_file))[1][1:].lower()

    info = {
        'bitrate': random.randint(1000, 500000),
        'size': random.randint(1000, 500000),
        'duration': random.randint(10, 50),
    }

    if ext in settings.AUDIO_CONTAINERS:
        info.update({
            'audio_codec': random.choice(list(settings.AUDIO_CODECS.keys())),
            'audio_bitrate': 192000,
            'audio_channels': 2,
        })
    elif ext in settings.VIDEO_CONTAINERS:
        info.update({
            'audio_codec': random.choice(list(settings.AUDIO_CODECS.keys())),
            'audio_bitrate': 192000,
            'audio_channels': 2,
            'video_codec': random.choice(list(settings.VIDEO_CODECS.keys())),
            'video_bitrate': 1000000,
            'video_width': 1920,
            'video_height': 1080,
        })
    else:
        raise Exception('Unknown input file format: {}'.format(input_file))

    return info


def get_mock_media_file(file_name, media_file_cls, formats=None):
    """
    Returns mock media file model with attached streams if formats is not None.

    :param file_name:
    :param media_file_cls: Audio or Video class.
    :param formats: list of streams formats.
    :return:
    """
    def mock_save(self, name, content):
        return name

    file_mock = mock.MagicMock(spec=File)
    file_mock.name = file_name
    file_mock.path = file_name

    mock_file = mock.MagicMock(spec=mock.sentinel.file_spec)
    mock_file.size = 1
    mock_file.name = file_name
    mock_open = mock.MagicMock(return_value=mock_file)

    def dummy_func(*args, **kwargs):
        pass

    with mock.patch.object(FileSystemStorage, 'save', mock_save):
        with mock.patch('avlogue.models.open', mock_open):
            with mock.patch.object(default_encoder, 'get_file_info', get_file_info):
                with mock.patch.object(default_encoder, 'get_file_preview', dummy_func):
                    media_file = media_file_cls.objects.create_from_file(file_mock)
                    if formats is not None:
                        for format in formats:
                            stream_info = get_file_info(file_name)
                            if media_file_cls == Video:
                                if format.video_bitrate is not None:
                                    stream_info['bitrate'] = format.video_bitrate
                                    stream_info['video_bitrate'] = format.video_bitrate
                                stream_info['video_codec'] = format.video_codec
                            if media_file_cls in (Audio, Video):
                                if format.audio_bitrate is not None:
                                    stream_info['bitrate'] = format.audio_bitrate
                                    stream_info['audio_bitrate'] = format.audio_bitrate
                                stream_info['audio_codec'] = format.audio_codec

                            stream = media_file.streams.model(media_file=media_file, file=file_mock, format=format,
                                                              **stream_info)
                            stream.save()
                            media_file.streams.add(stream)

    return media_file
