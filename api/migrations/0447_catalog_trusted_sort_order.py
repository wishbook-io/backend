# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0446_shipment_logistics_provider'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='trusted_sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
