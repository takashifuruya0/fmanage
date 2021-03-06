# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-15 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total', models.IntegerField()),
                ('buying_power', models.IntegerField()),
                ('stocks_value', models.IntegerField()),
                ('other_value', models.IntegerField()),
                ('investment', models.IntegerField()),
            ],
        ),
    ]
