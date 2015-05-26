__author__ = 'apalii'

from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^main/$', 'tz.views.main'),
                       url(r'^convert/$', 'tz.views.convert'),
                       #url(r'^getcityid/(?P<city_symbols>\w+)/$', 'tz.views.get_city_id'),
                       url(r'^getcityid/$', 'tz.views.get_city_id'),
)
