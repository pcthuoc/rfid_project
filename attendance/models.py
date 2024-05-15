from import_export import resources
from django.db import models
import datetime
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
# Create your models here.
class Student(models.Model):
    card_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    masv = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=7, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True) 

    def __str__(self):
        if self.name is None:
            return str(self.card_id)
        else:
            return str(self.name) + ' : ' + str(self.masv)

class Log(models.Model):
    ida = models.IntegerField(default=1)
    card_id = models.IntegerField()
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True, null=True)
    masv = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(default=datetime.datetime.now())
    time_in = models.TimeField(default=datetime.datetime.now())
    time_out = models.TimeField(blank=True, null=True)
    status = models.TextField(max_length=100)

    def __str__(self):
        return str(self.name) + ' : ' + str(self.date)

