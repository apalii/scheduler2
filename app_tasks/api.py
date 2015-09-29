from tastypie.resources import ModelResource
from app_tasks.models import Task
import datetime
'''
domain +
/tasks/api/task/?format=json - all
/tasks/api/task/3/?format=json - particular
/tasks/api/task/?format=json&task__contains=smth - search example
'''
class TaskAll(ModelResource):
    class Meta:
        queryset = Task.objects.all()
        resource_name = 'all'
        filtering = {
            'task': 'contains'
        }
        #fields = ['username', 'first_name', 'last_name', 'last_login']
        excludes = ['added', 'ip_addr', 'id']
        allowed_methods = ['get']


class Shift(ModelResource):
    class Meta:
        today = datetime.date.today()
        today_8 = datetime.datetime(today.year, today.month, today.day, 8, 0, 0)
        tomorrow = today_8 + datetime.timedelta(days=1)
        queryset = Task.objects.filter(
            date__gte=today_8
        ).exclude(
            date__gte=tomorrow
        ).order_by('-date')
        resource_name = 'shift'
        filtering = {
            'task': 'office'
        }
        #fields = ['username', 'first_name', 'last_name', 'last_login']
        excludes = ['added', 'ip_addr', 'id']
        allowed_methods = ['get']
        