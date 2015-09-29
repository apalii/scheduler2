from django.shortcuts import redirect, render_to_response
from django.core.context_processors import csrf
from django.http import HttpResponse, Http404
from app_tasks.models import City
#from django.core import serializers
import json

def main(request):
    args = {}
    args['active'] = 'Zones'
    args.update(csrf(request))

    if request.method == 'GET':
        return render_to_response('tz.html', args)
    else:
        return redirect('/tz/main/')


def get_city_id(request):
    if request.method == 'GET':
        #print request.GET['q']
        symbols = request.GET['q']
        '''
        cities = City.objects.filter(city_name__startswith=symbols)
        data = serializers.serialize('json', cities)
        return HttpResponse(data, content_type='application/json')
    else:
        return redirect('/tz/main/')'''
        response = json.dumps([city.city_name
                               for city in City.objects.filter(city_name__startswith=symbols)])

        return HttpResponse(response, content_type='application/json')
    elif request.method == 'POST':
        base_url = 'http://www.timeanddate.com/worldclock/converted.html'
        date_post = request.POST['date']
        date = date_post.split()[0].replace('-', '')
        hour = date_post.split()[1].replace(':', '')
        try:
            city_id = City.objects.get(city_name=request.POST['city'].lower()).city_id
        except City.DoesNotExist:
            raise Http404("Choose city from the list !!!")
        params = '?iso={}T{}&p1={}&p2=367'.format(date, hour, city_id)
        return redirect(base_url + params)


def convert(request):
    return redirect('/')