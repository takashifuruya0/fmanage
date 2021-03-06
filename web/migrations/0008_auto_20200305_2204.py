# Generated by Django 2.2.9 on 2020-03-05 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_entry_num_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='is_closed',
            field=models.BooleanField(default=False, help_text='終了したEntryかどうか', verbose_name='Closed'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='is_simulated',
            field=models.BooleanField(default=False, verbose_name='Simulation'),
        ),
    ]
