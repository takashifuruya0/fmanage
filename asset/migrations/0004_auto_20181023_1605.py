# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-23 07:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0003_buyorders'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('num', models.IntegerField()),
                ('price', models.FloatField()),
                ('commission', models.IntegerField()),
                ('is_nisa', models.BooleanField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asset.Stocks')),
            ],
        ),
        migrations.RenameField(
            model_name='holdingstocks',
            old_name='average_price',
            new_name='price',
        ),
    ]
