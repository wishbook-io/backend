# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0255_auto_20161005_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2016, 10, 5, 10, 32, 26, 639676, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2016, 10, 5, 10, 32, 32, 450525, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
