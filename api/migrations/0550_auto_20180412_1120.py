# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0549_auto_20180409_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='job_type',
            field=models.CharField(max_length=50, choices=[(b'Buyer', b'Buyer'), (b'Supplier', b'Supplier'), (b'Sales Order CSV', b'Sales Order CSV'), (b'Shipment Sales Order CSV', b'Shipment Sales Order CSV'), (b'SKU Map CSV', b'SKU Map CSV'), (b'Company Map CSV', b'Company Map CSV')]),
        ),
    ]
