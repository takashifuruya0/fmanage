# Generated by Django 2.2.9 on 2020-03-15 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_sbialert'),
    ]

    operations = [
        migrations.AddField(
            model_name='sbialert',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
