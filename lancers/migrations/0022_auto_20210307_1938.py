# Generated by Django 2.2.16 on 2021-03-07 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lancers', '0021_auto_20210307_1746'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientprofile',
            options={'verbose_name': 'クライアントプロファイル', 'verbose_name_plural': 'クライアントプロファイル'},
        ),
        migrations.AlterField(
            model_name='clientprofile',
            name='goal',
            field=models.CharField(blank=True, choices=[('1. 学習', '1. 学習'), ('2. アプリ作成', '2. アプリ作成'), ('3. 副業', '3. 副業'), ('4. 就職', '4. 就職')], max_length=255, null=True, verbose_name='目的'),
        ),
    ]
