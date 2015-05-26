from django.conf.urls import patterns, include, url
from django.contrib import admin
from api import TaskAll, Shift
from tastypie.api import Api

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(TaskAll())
v1_api.register(Shift())
'''
urlpatterns = patterns('',
    # The normal jazz here...
    (r'^blog/', include('myapp.urls')),
    (r'^api/', include(v1_api.urls)),
)
'''

urlpatterns = patterns('',
                       url(r'^$', 'app_tasks.views.main_page'),
                       url(r'^docs', 'app_tasks.views.docs'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'),
                       url(r'^task/', include('app_tasks.urls')),
                       url(r'^tasks/', include('app_tasks.urls')),
                       url(r'^tz/', include('tz.urls')),
                       url(r'^api/', include(v1_api.urls)),
                       )
