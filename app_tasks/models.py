from django.db import models

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
    ticket = models.CharField(max_length=30)
    date = models.DateTimeField()
    added = models.DateTimeField(auto_now_add=True)
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