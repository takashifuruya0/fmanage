# Generated by Django 2.2.16 on 2020-12-29 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lancers', '0014_opportunity_is_regular'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='name_slack',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Slackユーザ名'),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='is_copied_to',
            field=models.BooleanField(default=False, verbose_name='【定期案件】次期作成済み'),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='original_opportunity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='copied_opportunity', to='lancers.Opportunity', verbose_name='初期案件'),
        ),
    ]