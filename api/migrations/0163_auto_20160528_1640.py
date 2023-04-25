# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0162_salesorder_dispatch_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user',
            name='full_catalog_orders_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='selection',
            name='buyable',
            field=models.BooleanField(default=True),
        ),
    ]
