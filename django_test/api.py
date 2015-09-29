from tastypie.resources import ModelResource
from app_tasks.models import Task
from datetime import datetime as dt
import datetime 
import copy

# version 1 
class TaskAll(ModelResource):
    class Meta:
        queryset = Task.objects.all().order_by('-date')
        resource_name = 'all'
        filtering = {
            'task': 'contains'
        }
        #fields = ['username', 'first_name', 'last_name', 'last_login']
        excludes = ['added', 'ip_addr', 'id']
        allowed_methods = ['get']

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['current_time_utc'] = dt.strftime(dt.utcnow(), '%Y-%m-%d %H:%M') 
        return data

    
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
            'office': 'exact'
        }
        #fields = ['username', 'first_name', 'last_name', 'last_login']
        excludes = ['added', 'ip_addr', 'id']
        allowed_methods = ['get']

        
    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])
                # Rename the objects.
                data_dict['shift'] = copy.copy(data_dict['objects'])
                del(data_dict['objects'])
        return data_dict