# Generated by Django 2.2.9 on 2020-03-28 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_sbialert_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='is_in_order',
            field=models.BooleanField(default=False, help_text='NAMSから注文中か？', verbose_name='注文中'),
        ),
    ]
