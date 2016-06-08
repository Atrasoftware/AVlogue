from django.shortcuts import render_to_response

from avlogue.models import Video, Audio


def example_page(request):
    context = {
        'video': Video.objects.first(),
        'audio': Audio.objects.first(),
    }
    return render_to_response('example_app/example_view.html', context)
