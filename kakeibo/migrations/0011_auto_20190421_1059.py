# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-04-21 01:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0010_auto_20190421_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basemodel',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 4, 21, 1, 59, 35, 826703, tzinfo=utc)),
        ),
    ]