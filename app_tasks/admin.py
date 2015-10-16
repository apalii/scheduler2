__author__ = 'apalii'

from django.contrib import admin
from app_tasks.models import Task, Comment, Customer

class TaskInline(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ['comment']

class TaskAdmin(admin.ModelAdmin):
    #fields = ['task_ticket', 'task_date', 'task_status']
    inlines = [TaskInline]


admin.site.register(Task, TaskAdmin)
admin.site.register(Customer)
