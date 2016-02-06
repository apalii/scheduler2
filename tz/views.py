from django.shortcuts import redirect, render_to_response, render
from django.core.context_processors import csrf
from django.http import HttpResponse, Http404, JsonResponse
from app_tasks.models import City


def main(request):
    args = {}
    args['active'] = 'Zones'
    args.update(csrf(request))
    if request.method == 'GET':
        return render(request, 'tz.html', args)
    else:
        return redirect('/tz/main/')


def get_city_id(request):
    if request.method == 'GET':
        symbols = request.GET['q']
        response = [
            city.city_name for city in City.objects.filter(
                city_name__startswith=symbols
            )
        ]
        return JsonResponse(response, safe=False)
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