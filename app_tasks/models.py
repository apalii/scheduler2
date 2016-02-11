from django.db import models
from django.contrib.auth.models import User

'''
Migrations :
makemigrations Application # create migration
migrate                    # apply migration
sqlmigrate                 # displays the SQL statements for a migration.
'''

class Customer(models.Model):

    cust_rtid = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)

    class Meta():
        db_table = "customer"

    def __unicode__(self):
        return "{} : {}".format(self.name, self.cust_rtid)


class Engineer(models.Model):

    OFFICES = (
        (u'c', u'Chernihiv'),
        (u'k', u'Kyiv'),
        (u's', u'Sumy'),
    )

    POSITIONS = (
        (u'jse', u'Junior Support Engineer'),
        (u'mse', u'Middle Support Engineer'),
        (u'sse', u'Senior Support Engineer'),
        (u'tm', u'Team Lead'),
        (u'u', u'unspecified')
    )

    user = models.OneToOneField(User)
    office = models.CharField(choices=OFFICES, max_length=1, default='c')
    position = models.CharField(choices=POSITIONS, max_length=3, default='u')


class Task(models.Model):

    STATUSES = (
        (u'Scheduled', u'Scheduled'),
        (u'Done', u'Done'),
        (u'In progress', u'In progress'),
        (u'Postponed', u'Postponed'),
        (u'Partially', u'Partially'),
        (u'Cancelled', u'Cancelled'),
        (u'Failed', u'Failed'),
    )

    task_user = models.ForeignKey(User, related_name="task_user_id", default="1")
    ticket = models.CharField(max_length=30)
    date = models.DateTimeField()
    added = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=33, default="Unknown")
    customer = models.CharField(max_length=30)
    customer_id = models.CharField(max_length=5, blank=True)
    task = models.CharField(max_length=200)
    executor = models.CharField(max_length=20, default="Nobody")
    status = models.CharField(max_length=20, choices=STATUSES, default='Scheduled')
    office = models.IntegerField(default=0)
    ip_addr = models.GenericIPAddressField(default="0.0.0.0")


    def __unicode__(self):
        return "{} : {}".format(str(self.id), self.ticket)

    class Meta():
        db_table = 'task'


class Comment(models.Model):

    comment = models.TextField(max_length=800)
    comments_task = models.ForeignKey(Task)
    added = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=33, default="Unknown")

    class Meta():
        db_table = 'comment'
        ordering = ['added']


class City(models.Model):

    city_name = models.CharField(max_length=100)
    city_id = models.CharField(max_length=4)

    class Meta():
        db_table = 'cities'

    def __unicode__(self):
        return "{} : {}".format(self.city_name, self.city_id)


class Ips(models.Model):

    ip = models.GenericIPAddressField(default="0.0.0.0")
    region = models.CharField(max_length=100)
    counter = models.IntegerField(default=1)

    def __unicode__(self):
        return "{} : {}".format(str(self.counter), str(self.ip))

    class Meta():
        db_table = 'ips'
