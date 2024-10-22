from import_export import resources
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Student(models.Model):
    class_name = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    masv = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=7, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    finger_id = models.IntegerField( default=0)

    def __str__(self):
        if self.name is None:
            return str(self.id)
        else:
            return f"{self.name} : {self.masv}"

class Log(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Liên kết với Student
    date = models.DateTimeField(default=timezone.now)
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(blank=True, null=True)
    status = models.TextField(max_length=100)

    def __str__(self):
        return f"{self.student.name} : {self.date}"

@receiver(post_delete, sender=Student)
def delete_student_logs(sender, instance, **kwargs):
    Log.objects.filter(student=instance).delete()
