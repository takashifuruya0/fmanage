# Generated by Django 2.2.24 on 2021-07-19 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0028_auto_20210719_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='is_listed',
            field=models.BooleanField(default=True, verbose_name='上場済み'),
        ),
        migrations.AlterField(
            model_name='ipo',
            name='datetime_close',
            field=models.DateTimeField(blank=True, null=True, verbose_name='ブックビル終了日時'),
        ),
    ]
