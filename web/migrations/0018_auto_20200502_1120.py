# Generated by Django 2.2.9 on 2020-05-02 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0017_entrystatus_entry_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='val',
            field=models.FloatField(help_text='株価/投資信託単価'),
        ),
    ]