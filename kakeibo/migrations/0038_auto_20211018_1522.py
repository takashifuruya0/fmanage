# Generated by Django 2.2.24 on 2021-10-18 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0037_auto_20211018_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronkakeibo',
            name='fee',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='usualrecord',
            name='fee',
            field=models.FloatField(),
        ),
    ]
