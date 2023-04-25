# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0362_auto_20170628_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushsellerprice',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 28, 13, 28, 54, 212064, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
