# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-05-14 23:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0014_auto_20190510_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsualRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.IntegerField()),
                ('way', models.CharField(max_length=20)),
                ('memo', models.CharField(blank=True, max_length=100, null=True)),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('move_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ur_move_from', to='kakeibo.Resources')),
                ('move_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ur_move_to', to='kakeibo.Resources')),
                ('usage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kakeibo.Usages')),
            ],
        ),
    ]
