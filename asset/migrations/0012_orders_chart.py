# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-05-15 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0011_auto_20190510_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='chart',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]