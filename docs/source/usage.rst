Usage examples
==============

Before usage, an application must prepare a list of needed formats::

    from avlogue.models import FormatSet, Format

    f1 = VideoFormat(
        name="h264 720p",
        container="mp4",
        audio_codec="aac",
        audio_bitrate=128000,
        video_codec="h264",
        video_codec_params="-profile:v main -level 3.1",
        video_bitrate=1000000,
        video_width=null,
        video_height=720,
        video_aspect_mode="scale"
    )
    f2 = VideoFormat(
      name="vp8 WebM",
      container="webm",
      audio_codec="vorbis",
      video_codec="vp8",
      video_bitrate=1000000,
      video_codec_params="-quality good -cpu-used 0 -qmin 10 -qmax 42"    
    )

    format_set = VideoFormatSet(name='Sample format set')
    format_set.formats.add([f1, f2])


After a file has been uploaded, AVlogue must be told about it::

    from avlogue.models import Video

    video = Video.objects.create_from_file(file=video_file, title='video title', slug='video-file')

    # or

    video = Video.objects.create_from_file(file=video_file_path)

Title and slug arguments are optional::

    conversion_task = video.convert([video_format1, video_format2, ...])
    streams = conversion_task.get()

Convert will create or update video streams specified by list of video formats.
Streams with higher quality will be ignored during conversion.


After the conversion::

    all_streams = video.streams.all()
    stream = video.streams.get(format=SomeFormat)
    streams = video.streams.filter(format__container='avi')


In templates::

    {% load avlogue_tags %}

    {% avlogue_player video formats='vp8 WebM, h264 360p' %}

    {% avlogue_player video format_sets='Sample format set' %}

Will produce::

    <video class="avlogue-player avlogue-video avlogue-video-1" controls="controls">

        <source src="/media/avlogue/video/streams/sample3_h264-360p.mp4" type="video/mp4">

        <source src="/media/avlogue/video/streams/sample3_vp8-webm.webm" type="video/webm">

        Your browser does not support the video tag.
    </video>
