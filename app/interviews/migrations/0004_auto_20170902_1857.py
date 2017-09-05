# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-02 18:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0003_auto_20170830_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='vacancies.Vacancy'),
        ),
    ]