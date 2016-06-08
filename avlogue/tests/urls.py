"""URLs to run the tests."""
from distutils.version import StrictVersion

from compat import patterns, include, url
import django
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()
django_version = django.get_version()

urls = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^example-page', include('avlogue.tests.example_app.urls')),
]

if StrictVersion(django_version) < StrictVersion('1.9'):
    urlpatterns = patterns('', *urls)
else:
    urlpatterns = urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
