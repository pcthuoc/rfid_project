# Generated by Django 3.2.12 on 2024-05-14 07:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0006_auto_20240514_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 5, 14, 7, 9, 23, 111190)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time_in',
            field=models.TimeField(default=datetime.datetime(2024, 5, 14, 7, 9, 23, 111200)),
        ),
    ]
