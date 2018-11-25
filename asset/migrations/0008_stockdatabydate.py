# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-25 09:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0007_auto_20181116_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockDataByDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('val_start', models.FloatField()),
                ('val_high', models.FloatField()),
                ('val_low', models.FloatField()),
                ('val_end', models.FloatField()),
                ('turnover', models.IntegerField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asset.Stocks')),
            ],
        ),
    ]
