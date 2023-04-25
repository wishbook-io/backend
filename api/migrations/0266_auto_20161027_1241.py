# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0265_auto_20161027_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='openingstock',
            name='date',
            field=models.DateField(default=datetime.datetime(2016, 10, 27, 7, 11, 2, 209814, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='openingstock',
            name='remark',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
