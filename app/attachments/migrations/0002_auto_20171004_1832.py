# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-04 18:32
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='data',
            field=easy_thumbnails.fields.ThumbnailerField(upload_to=''),
        ),
    ]
