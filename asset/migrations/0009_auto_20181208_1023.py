# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-08 01:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0008_stockdatabydate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocks',
            name='code',
            field=models.CharField(max_length=8, unique=True),
        ),
    ]