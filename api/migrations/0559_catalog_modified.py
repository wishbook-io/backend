# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0558_auto_20180421_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 43, 22, 204256, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
