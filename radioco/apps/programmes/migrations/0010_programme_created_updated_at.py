# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0009_programme_remove_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime.fromtimestamp(0), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='programme',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime.fromtimestamp(0), auto_now=True),
            preserve_default=False,
        ),
    ]
