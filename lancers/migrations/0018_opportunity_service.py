# Generated by Django 2.2.16 on 2021-02-23 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lancers', '0017_auto_20210223_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='lancers.Service', verbose_name='サービス'),
        ),
    ]
