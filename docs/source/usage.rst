Usage examples
==============

Before usage, an application must prepare a list of needed formats::

    from avlogue.models import FormatSet, Format
    from avlogue.formats import AVI, MP4, MKV, AIFF, WAV, r720, r360p, h264, mp3, ac3

    format_set = VideoFormatSet(name='xyz')

    f1 = VideoFormat(container=AVI, vcodec=h264, vformat=r720p, acodec=mp3,
        video_bitrate=2200, audio_bitrate=128, max_ac=2)
    f2 = VideoFormat(container=AVI, vcodec=h264, vformat=r720p, acodec=ac3,
        video_bitrate=2200, audio_bitrate=128, max_ac=6)
    format_set.add([f1, f2])


After a file has been uploaded, AVlogue must be told about it::

    from avlogue.models import VideoFile

    video = VideoFile(source_file=XXXXXX)  # XXXXX is an instance of django.core.files.File
    conversion_task = video.convert(format_set)

    # signals?

After the conversion::

    mediafile.html_block()

    mediafile.streams()

    mediafile.streams(container=AVI)


