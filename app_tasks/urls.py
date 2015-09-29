__author__ = 'apalii'

from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^all/$', 'app_tasks.views.tasks'),
                       url(r'^shift/$', 'app_tasks.views.shift'),
                       url(r'^month/$', 'app_tasks.views.month'),
                       url(r'^addtask/$', 'app_tasks.views.add_task'),
                       url(r'^addcomment/(?P<task_id>\d+)/$', 'app_tasks.views.addcomment'),
                       url(r'^changestatus/(?P<task_id>\d+)/$', 'app_tasks.views.change_status'),
                       url(r'^changeowner/$', 'app_tasks.views.change_executor'),
                       url(r'^delete/(?P<task_id>\d+)/$', 'app_tasks.views.delete_task'),
                       url(r'^adding/$', 'app_tasks.views.add_task'),
                       url(r'^getcustid/$', 'app_tasks.views.get_cust_id'),
                       url(r'^get/(?P<task_id>\d+)/$', 'app_tasks.views.task'),
                       url(r'^search/$', 'app_tasks.views.search_tasks'),
                       url(r'^neartask', 'app_tasks.views.nearest_task_json')
                       
)