# -*- coding: utf-8 -*-

import datetime
import json
import requests
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render_to_response, render
from django.db.models import Count
from app_tasks.models import Task, Comment, Customer, Log
from django.contrib.auth.models import User
from forms import CommentForm, StatusForm
from django.core.context_processors import csrf
from django.shortcuts import redirect, get_object_or_404
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.http import (
    require_http_methods, require_safe, require_POST
)
requests.packages.urllib3.disable_warnings()

def logging(task_id, message):
    task = Task.objects.get(pk=task_id)
    new_log = Log.objects.create(
        log_task=task, message=message, date=timezone.now()
    )


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
@cache_page(60)
def nearest_task_json(request, office_id):
    """
    As it was agreed for the intergration with Portarius(chorome addon) - was
    added 3 separate endpoints for the nearest tasks
    for every particular office.
    """
    now = timezone.now()
    office_id = int(office_id)
    office_map = {
        1: "kyiv",
        2: "chernihiv",
        3: "sumy",
    }
    try:
        near_task = Task.active.filter(
            date__gt=now).filter(
            office=office_id).order_by('date').values().first()
    except IndexError:
        near_task = "There are no nearest tasks"
    near_tasks = {
        office_map[office_id]: near_task,
    }
    return JsonResponse(near_tasks)


@require_safe
@login_required
def main_page(request):
    now = timezone.now()
    user = User.objects.get(id=request.user.id)
    office = user.engineer.office
    try:
        if office:
            near_task = Task.active.filter(
                date__gt=now).filter(office=office).order_by('date').first()
        else:
            near_task = Task.active.filter(
                date__gt=now).filter(office=2).order_by('date').first()
    except IndexError:
        near_task = None
    context = {
        'active': 'Home',
        'near_task': near_task,
    }
    return render(request, 'main.html', context)


@require_safe
@login_required
def shift(request):
    """
    Day shift from 08-00 to 20-00
    Night shift from 20-00 to 8-00
    """
    today = datetime.date.today()
    now = datetime.datetime.now()
    user = User.objects.get(id=request.user.id)
    office = user.engineer.office
    if now.hour >= 8 and now.hour < 20:
        # case from 08-00 to 20-00 day shift
        day = True
        today_8 = datetime.datetime(
            today.year, today.month, today.day, 8, 0, 0)
        today_20 = datetime.datetime(
            today.year, today.month, today.day, 20, 0, 0)
        tasks = Task.active.filter(
            date__range=(today_8, today_20)).order_by('-date')

    elif now.hour >= 20:
        # case from 20-00 to 23-00 night shift
        day = False
        today_20 = datetime.datetime(
            today.year, today.month, today.day, 20, 0, 0)
        tomorrow = today_20 + datetime.timedelta(hours=12)
        tasks = Task.active.filter(
            date__range=(today_20, tomorrow)).order_by('date')

    elif now.hour >= 0 and now.hour < 8:
        # case from 00-00 to 08-00 night shift
        day = False
        yesterday_20 = datetime.datetime(
            today.year, today.month, today.day - 1, 20, 0, 0)
        tomorrow = yesterday_20 + datetime.timedelta(hours=12)
        tasks = Task.active.filter(
            date__range=(yesterday_20, tomorrow)).order_by('date')

    nearest = Task.active.filter(date__gt=now).order_by('date')[0:3]
    """
    If an office is undefined(equals 0) - show all the tasks
    Else show tasks only for particular office
    """
    tasks_per_office = tasks.filter(office=office) if office else tasks
    """
    Adding comments counting according to
    https://docs.djangoproject.com/en/1.7/topics/db/aggregation/#cheat-sheet
    """
    tasks_and_comments = tasks_per_office.annotate(
        comments=Count('comment')
    )
    context = {
        'active': 'Shift',
        'nearest': nearest,
        'tasks': tasks_and_comments,
        'day': day
    }
    return render(request, 'shift.html', context)


class TasksNew(ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'


    def get_queryset(self):
        now = timezone.now()
        qs = Task.active.exclude(date__lt=now).order_by('date')
        return qs


    def get_context_data(self, **kwargs):
        context = super(TasksNew, self).get_context_data(**kwargs)
        new = self.request.session.pop('new', None)
        context.update({'active': 'Tasks',
                       'class': self.__class__.__name__,
                        'new': new,
                       })
        return context


class TasksOld(TasksNew):
    paginate_by = 25
    paginate_orphans = 2

    def get_queryset(self):
        now = timezone.now()
        qs = Task.active.filter(date__lt=now).order_by('-date')
        return qs


@login_required
def month(request):
    this_month = timezone.now().month
    tasks = Task.active.filter(date__month=this_month).order_by('date')
    return render(
        request, 'month.html', {'month': tasks, 'active': 'Month'}
    )


@login_required
def task(request, task_id=1):
    comment_form = CommentForm
    status_form = StatusForm
    context = {}
    context.update(csrf(request))
    context['form'] = comment_form
    context['status_form'] = status_form
    context['task'] = get_object_or_404(Task, id=task_id)
    context['comments'] = Comment.objects.filter(
        comments_task_id=task_id)
    context['added_by'] = Task.objects.get(id=task_id).added_by
    context['logs'] = Log.objects.filter(log_task=task_id).order_by('-date')
    return render(request, 'task.html', context)


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
    old_field_clened = timezone.localtime(old_field).__str__()[
        :old_field.__str__().find('+')] if field == 'date' else old_field
    new_field = request.POST[field]
    task = Task.objects.get(pk=task_id)
    setattr(task, field, new_field)
    task.save(update_fields=[field])
    to_log = "{} was changed from {} to {} by {}".format(
        field, old_field_clened, new_field, request.user
    )
    logging(task.id, to_log)
    return HttpResponse('')


@require_POST
@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.is_deleted = True
    task.save(update_fields=['is_deleted'])
    to_log = "Task(id={}): '{}' was deleted by {}".format(
        task.id, task.task, request.user
    )
    new_log = Log.objects.create(
        log_task=task, message=to_log, date=timezone.now()
    )
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
        context = {}
        context.update(csrf(request))
        context['active'] = 'Add'
        return render(request, 'addtask.html', context)
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
            context = {'message': 'Choose customer from the list !',
                    'path': path
                    }
            return render(request, '404.html', context)

        if datetime.datetime.strptime(post_data, '%Y-%m-%d %H:%M') <= now:
            context = {'message': 'Timeframe in the past !',
                    'path': path
                    }
            return render(request, '404.html', context)

        elif request.POST['office'] not in ['0', '1', '2', '3']:
            context = {'message': 'Please choose appropriate office !',
                    'path': path
                    }
            return render(request, '404.html', context)

        elif 'update' in request.POST['task'].lower() and \
             'from' in request.POST['task'].lower():
            # update during range +-4 hours
            time_before = tz_date - timezone.timedelta(hours=4)
            time_after  = tz_date + timezone.timedelta(hours=4)
            print time_before, time_after
            # lookup for nearest updates
            update_near = Task.active.exclude(
                date__lt=time_before).exclude(date__gt=time_after).filter(
                task__contains='update').filter(task__contains='from')
            print update_near
            # update during shifts
            shift = 'day' if tz_date.hour > 8 and tz_date.hour < 20 else 'night'
            day_start = timezone.datetime(tz_date.year, tz_date.month, tz_date.day, 8, 0, 0)
            day_end = timezone.datetime(tz_date.year, tz_date.month, tz_date.day, 20, 0, 0)
            tomorrow = day_start + datetime.timedelta(days=1)

            # lookup for day/night shift
            update_shift = Task.active.exclude(
                date__lt=day_start).exclude(date__gt=day_end).filter(
                task__contains='update') if shift == 'day' else \
            Task.active.exclude(
                date__lt=tomorrow).exclude(date__gt=day_end).filter(
                task__contains='update').filter(task__contains='from')

        if update_near or update_shift:
            msg = 'Another update exists. Press backspace and try another date'
            context = {'message': msg,
                    'updates': update_near,
                    'update_shift': update_shift,
                    'path': path,
                   }
            return render(request, '404.html', context)

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
            request.session['new'] = newtask.id
            return redirect('new')


@require_http_methods(["GET", "POST"])
@login_required
def search_tasks(request):
    if request.method == 'GET':
        context = {}
        context.update(csrf(request))
        context['active'] = 'Search'
        return render(request, 'search.html', context)
    if request.method == 'POST':
        search_text = request.POST['search_text']
    else:
        search_text = ""
    tasks = Task.objects.filter(
        task__contains=search_text).order_by("-date")
    context = {'tasks': tasks}
    return render(request, 'ajax_search.html', context)


@require_safe
@login_required
@cache_page(3600 * 24)
def docs(request):
    history_url = 'https://api.github.com/repos/apalii/scheduler2/commits'
    context = {}
    context['version'] = '3.0 beta'
    context['history'] = requests.get(history_url).json()
    return render(request, 'docs.html', context)
