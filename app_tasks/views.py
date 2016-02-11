# -*- coding: utf-8 -*-

import datetime
import json
import requests
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render_to_response, render
from app_tasks.models import Task, Comment, Customer
from forms import CommentForm, StatusForm
from django.core.context_processors import csrf
from django.shortcuts import redirect, get_object_or_404
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import (
    require_http_methods, require_safe, require_POST
)

import logging
logr = logging.getLogger(__name__)

"""
def kurs_privat():
    '''Безналичный курс Приватбанка
    (конвертация по картам, Приват24, пополнение вкладов)
    '''
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=11'
    kurs = requests.get(url).json()[2]
    return 'buy {} | sale {}'.format(kurs['buy'], kurs['sale'])
    """

def get_ip(request):
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        ip = ""
    return ip


@require_safe
def nearest_task_json(request):
    now = timezone.now()
    near_task = Task.objects.filter(date__gt=now).order_by('date').values()[0]
    near_task['date'] = str(near_task['date'])
    near_task['added'] = str(near_task['added'])
    response = json.dumps(near_task)
    return JsonResponse(near_task)


@require_safe
@login_required
def main_page(request):
    now = timezone.now()
    try:
        near_task = Task.objects.filter(date__gt=now).order_by('date')[0]
    except IndexError:
        near_task = None
    args = {'active': 'Home','near_task': near_task}
    return render(request, 'main.html', args)


@require_safe
@login_required
def shift(request):
    today = datetime.date.today()
    today_8 = datetime.datetime(today.year, today.month, today.day, 8, 0, 0)
    tomorrow = today_8 + datetime.timedelta(days=1)
    today = Task.objects.filter(
        date__gte=today_8
    ).exclude(
        date__gte=tomorrow
    ).order_by('-date')
    nearest = Task.objects.filter(
        date__gt=datetime.datetime.now())[0:3]
    args = {
        'active': 'Shift',
        'today': today,
        'nearest': nearest
    }
    return render(request, 'today.html', args)


class TasksNew(ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'


    def get_queryset(self):
        now = timezone.now()
        qs = Task.objects.order_by('-date')
        return qs.exclude(date__lt=now)


    def get_context_data(self, **kwargs):
        context = super(TasksNew, self).get_context_data(**kwargs)
        context.update({'active': 'Tasks',
                       'class': self.__class__.__name__,
                       })
        return context


class TasksOld(TasksNew):
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        qs = Task.objects.filter(date__lt=now).order_by('-date')
        return qs


@login_required
def month(request):
    this_month = timezone.now().month
    tasks = Task.objects.filter(
        date__month=this_month).order_by('-date')
    return render(
        request, 'month.html', {'month': tasks, 'active': 'Month'}
    )


@login_required
def task(request, task_id=1):
    comment_form = CommentForm
    status_form = StatusForm
    args = {}
    args.update(csrf(request))
    args['form'] = comment_form
    args['status_form'] = status_form
    args['task'] = get_object_or_404(Task, id=task_id)
    args['comments'] = Comment.objects.filter(
        comments_task_id=task_id)
    args['added_by'] = Task.objects.get(id=task_id).added_by
    return render(request, 'task.html', args)


@require_POST
@login_required
def addcomment(request, task_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(
            comment=form.cleaned_data['comment'],
            comments_task_id=task_id,
            added_by=request.user
        )
    return redirect('/tasks/get/%s/' % task_id)


@require_POST
@login_required
def change_status(request, task_id):
    status_form = StatusForm(request.POST)
    if status_form.is_valid():
        Task.objects.filter(
            pk=task_id).update(
            status=status_form.cleaned_data['status'])
    return redirect('/tasks/get/%s/' % task_id)


@require_POST
@login_required
def change_field(request):
    task_id = request.POST['id']
    field = request.POST['field']
    if field == 'date':
        try:
            date = timezone.datetime.strptime(
                request.POST[field], '%Y-%m-%d %H:%M'
            )
        except ValueError:
            err = "Expected format : %Y-%m-%d %H:%M"
            return JsonResponse({'status': 'error', 'msg': err})
    old_field = Task.objects.get(pk=task_id).__dict__.get(field)
    new_field = request.POST[field]
    task = Task.objects.get(pk=task_id)
    setattr(task, field, new_field)
    task.save(update_fields=[field])
    logr.debug("{} was changed from {} to {} by {}".format(
            field, old_field, new_field, request.user))
    return HttpResponse('')


@require_POST
@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id).task
    instance = get_object_or_404(Task, id=task_id)
    instance.delete()
    logr.debug("Task with id {} was deleted by {}".format(
            task_id, request.user))
    logr.debug("Task content : {}".format(task))
    return redirect('add')


@require_safe
@login_required
def get_cust_id(request):
        symbols = request.GET['q']
        response = [
            customer.name for customer in Customer.objects.filter(
                name__contains=symbols
            )
        ]
        return JsonResponse(response, safe=False)


@require_http_methods(["GET", "POST"])
@login_required
def add_task(request):
    if request.method == 'GET':
        args = {}
        args.update(csrf(request))
        args['active'] = 'Add'
        return render(request, 'addtask.html', args)
    elif request.method == 'POST':
        post_data = request.POST['date']
        path = request.META.get('PATH_INFO')
        now = datetime.datetime.now()
        update_near = []
        update_shift = []
        try:
            tz_date = timezone.datetime.strptime(post_data, '%Y-%m-%d %H:%M')
        except ValueError:
            raise Http404("Incorrect data ! Expected format : %Y-%m-%d %H:%M")
        try:
            cust_inc = Customer.objects.get(name=request.POST['customer'])
        except Customer.DoesNotExist:
            args = {'message': 'Choose customer from the list !',
                    'path': path
                    }
            return render(request, '404.html', args)

        if datetime.datetime.strptime(post_data, '%Y-%m-%d %H:%M') <= now:
            args = {'message': 'Timeframe in the past !',
                    'path': path
                    }
            return render(request, '404.html', args)

        elif request.POST['office'] not in ['0', '1', '2', '3']:
            args = {'message': 'Please choose appropriate office !',
                    'path': path
                    }
            return render(request, '404.html', args)

        elif 'update' in request.POST['task'].lower() and \
             'from' in request.POST['task'].lower():
            # update during range +-4 hours
            time_before = tz_date - timezone.timedelta(hours=4)
            time_after  = tz_date + timezone.timedelta(hours=4)

            # lookup for nearest updates
            update_near = Task.objects.exclude(
                date__lt=time_before
            ).exclude(
                date__gt=time_after
            ).filter(
                task__contains='update'
            ).filter(
                task__contains='from')

            # update during shifts
            shift = 'day' if tz_date.hour > 8 and tz_date.hour < 20 else 'night'
            day_start = timezone.datetime(tz_date.year, tz_date.month, tz_date.day, 8, 0, 0)
            day_end = timezone.datetime(tz_date.year, tz_date.month, tz_date.day, 20, 0, 0)
            tomorrow = day_start + datetime.timedelta(days=1)

            # lookup for day/night shift
            update_shift = Task.objects.exclude(
                date__lt=day_start
            ).exclude(
                date__gt=day_end
            ).filter(
                task__contains='update') if shift == 'day' else \
            Task.objects.exclude(
                date__lt=tomorrow
            ).exclude(
                date__gt=day_end
            ).filter(
                task__contains='update'
            ).filter(
                task__contains='from')

        if update_near or update_shift:
            msg = 'Another update exists. Press backspace and try another date'
            args = {'message': msg,
                    'updates': update_near,
                    'update_shift': update_shift,
                    'path': path,
                   }
            return render(request, '404.html', args)

        else:
            owner = "Nobody" if not request.POST['executor'] else request.POST['executor']
            newtask = Task.objects.create(ticket=request.POST['ticket'],
                                          date=request.POST['date'],
                                          customer=cust_inc.short_name,
                                          customer_id=cust_inc.cust_rtid,
                                          task=request.POST['task'],
                                          executor=owner,
                                          office=request.POST['office'],
                                          ip_addr=get_ip(request),
                                          added_by = request.user,
                                          )
            return redirect('/tasks/get/%s/' % newtask.id)


@require_http_methods(["GET", "POST"])
@login_required
def search_tasks(request):
    if request.method == 'GET':
        args = {}
        args.update(csrf(request))
        args['active'] = 'Search'
        return render(request, 'search.html', args)
    if request.method == 'POST':
        search_text = request.POST['search_text']
    else:
        search_text = ""
    tasks = Task.objects.filter(
        task__contains=search_text).order_by("-date")
    args = {'tasks': tasks}
    return render(request, 'ajax_search.html', args)


@require_safe
@login_required
def docs(request):
    args = {}
    args['version'] = '3.0 beta'
    return render(request, 'docs.html', args)
# ----------------------------------------------------------------
