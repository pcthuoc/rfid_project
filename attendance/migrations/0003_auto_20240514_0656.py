# Generated by Django 3.2.12 on 2024-05-14 06:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_alter_log_time_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 5, 14, 6, 56, 17, 134661)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time_in',
            field=models.TimeField(default=datetime.datetime(2024, 5, 14, 6, 56, 17, 134683)),
        ),
    ]
