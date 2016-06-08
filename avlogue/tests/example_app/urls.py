from django.conf.urls import patterns, url

from views import example_page

urlpatterns = patterns('', url(r'^$', example_page, ))
