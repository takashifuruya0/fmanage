# Generated by Django 2.2.9 on 2020-04-11 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20200329_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='val_plan',
            field=models.FloatField(blank=True, help_text='予定Entry株価', null=True, verbose_name='予定Entry株価'),
        ),
    ]
