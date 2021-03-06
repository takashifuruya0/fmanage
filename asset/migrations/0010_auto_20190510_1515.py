# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-05-10 06:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0009_auto_20181208_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryExit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entry', models.DateField()),
                ('chart_entry', models.ImageField(upload_to='images/')),
                ('price_entry', models.FloatField()),
                ('num_entry', models.IntegerField()),
                ('price_set_profit', models.FloatField()),
                ('price_loss_cut', models.FloatField()),
                ('date_exit', models.DateField()),
                ('chart_exit', models.ImageField(upload_to='images/')),
                ('price_exit', models.FloatField()),
                ('num_exit', models.IntegerField()),
                ('commission', models.IntegerField()),
                ('memo', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ReasonLose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='entryexit',
            name='reason_lose',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asset.ReasonLose'),
        ),
        migrations.AddField(
            model_name='entryexit',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asset.Stocks'),
        ),
    ]
