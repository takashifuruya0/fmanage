# Generated by Django 2.2.16 on 2020-11-06 05:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lancers', '0009_auto_20201027_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='sync_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='連携ID'),
        ),
        migrations.AddField(
            model_name='client',
            name='sync_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='連携ID'),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='sync_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='連携ID'),
        ),
        migrations.AddField(
            model_name='opportunitywork',
            name='sync_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='連携ID'),
        ),
        migrations.AlterField(
            model_name='opportunitywork',
            name='opportunity',
            field=models.ForeignKey(limit_choices_to={'type__in': ('直接受注', '提案受注')}, on_delete=django.db.models.deletion.CASCADE, to='lancers.Opportunity', verbose_name='案件'),
        ),
    ]
