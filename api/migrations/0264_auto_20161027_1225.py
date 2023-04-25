# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0263_push_user_product_viewed_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryadjustment',
            name='created_at',
        ),
        migrations.AddField(
            model_name='inventoryadjustment',
            name='date',
            field=models.DateField(default=datetime.datetime(2016, 10, 27, 6, 55, 42, 705162, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventoryadjustment',
            name='remark',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
