# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0319_product_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2017, 4, 8, 10, 32, 59, 827835, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2017, 4, 8, 10, 33, 3, 507925, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
