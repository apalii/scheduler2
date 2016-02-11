__author__ = 'apalii'

from django.contrib import admin
from app_tasks.models import Task, Comment, Customer, Engineer

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class TaskInline(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ['comment']

class TaskAdmin(admin.ModelAdmin):
    #fields = ['task_ticket', 'task_date', 'task_status']
    inlines = [TaskInline]


# Define an inline admin descriptor for Engineer model
# which acts a bit like a singleton
class EngineerInline(admin.StackedInline):
    model = Engineer
    can_delete = False
    verbose_name_plural = 'engineers'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EngineerInline, )


admin.site.register(Task, TaskAdmin)
admin.site.register(Customer)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)