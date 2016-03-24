__author__ = 'apalii'

from django.contrib import admin
from app_tasks.models import Task, Comment, Customer, Engineer, Log, City

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class TaskInline(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ['comment']

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'date', 'added_by', 'executor',
                    'customer', )
    list_filter = ('office', 'date', 'executor', 'added_by', 'customer')
    inlines = [TaskInline]
    search_fields = ('task', 'executor')


# Define an inline admin descriptor for Engineer model
# which acts a bit like a singleton
class EngineerInline(admin.StackedInline):
    model = Engineer
    can_delete = False
    verbose_name_plural = 'engineers'


class LogAdmin(admin.ModelAdmin):
    """
    log_task = models.ForeignKey(Task)
    message = models.CharField(max_length=300)
    date = models.DateTimeField()
    """
    list_display = ('message', 'date')

    def has_add_permission(self, request):
        return False


class LogInline(admin.StackedInline):
    model = Log
    can_delete = False
    verbose_name_plural = 'logs'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EngineerInline, )


admin.site.register(Task, TaskAdmin)
admin.site.register(Customer)
admin.site.register(City)
admin.site.register(Log, LogAdmin)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)