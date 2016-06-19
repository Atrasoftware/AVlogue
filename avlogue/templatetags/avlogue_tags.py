from django.template import Library

from avlogue.models import Audio, Video

register = Library()


@register.inclusion_tag('avlogue/player_tag.html')
def avlogue_player(media_file, formats=None, format_sets=None, bitrate=None, min_bitrate=None, max_bitrate=None,
                   **kwargs):
    """
    Player template tag for audio and video. Streams can be filtered by comma separated formats/format_sets names
    and bitrate value. Other kwargs params will be added to the template tag as attributes.

    :param media_file: Video or Audio
    :type media_file: avlogue.models.MediaFile
    :param formats: comma separated names of formats
    :type formats: str
    :param format_sets: comma separated names of format sets
    :type format_sets: str
    :param bitrate: streams bitrate
    :type bitrate: int
    :param min_bitrate: streams minimal bitrate
    :type min_bitrate: int
    :param max_bitrate: streams maximal bitrate
    :type max_bitrate: int
    :param kwargs: additional attributes for html element
    :return:
    """

    def filter_streams_by_formats(streams, formats):
        format_names = []
        for format_name in formats.split(','):
            format_names.append(format_name.strip())
        return streams.filter(format__name__in=format_names)

    def filter_streams_by_format_sets(streams, format_sets):
        format_set_names = []
        for format_set_name in format_sets.split(','):
            format_set_names.append(format_set_name.strip())
        return streams.filter(format__format_sets__name__in=format_set_names)

    def filter_streams_by_bitrate(streams, bitrate=None, min_bitrate=None, max_bitrate=None):
        if bitrate is not None:
            return streams.filter(bitrate=bitrate)
        if min_bitrate is not None:
            streams = streams.filter(bitrate__gte=min_bitrate)
        if max_bitrate is not None:
            streams = streams.filter(bitrate__lte=max_bitrate)
        return streams

    context = {}
    if isinstance(media_file, Audio):
        context['tag'] = 'audio'
    elif isinstance(media_file, Video):
        context['tag'] = 'video'
    else:
        raise TypeError('media_file must be instance of Audio or Video')
    context['media_file'] = media_file

    streams = media_file.streams
    if formats is not None:
        streams = filter_streams_by_formats(streams, formats)
    if format_sets is not None:
        streams = filter_streams_by_format_sets(streams, format_sets)
    streams = filter_streams_by_bitrate(streams, bitrate, min_bitrate, max_bitrate)

    context['streams'] = streams.all()

    attrs = {
        'controls': 'controls',
        'class': 'avlogue-player avlogue-{tag} avlogue-{tag}-{media_file_id}'.format(tag=context['tag'],
                                                                                     media_file_id=media_file.pk)
    }
    attrs.update(kwargs)
    context['attrs'] = attrs

    return context
