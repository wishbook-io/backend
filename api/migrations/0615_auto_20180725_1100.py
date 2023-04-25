# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0614_catalogeavflat_style'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountrule',
            name='all_brands',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='discountrule',
            name='discount_type',
            field=models.CharField(default=b'Public', max_length=20, choices=[(b'Public', b'Public'), (b'Private', b'Private')]),
        ),
        migrations.AlterField(
            model_name='discountrule',
            name='name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='jobs',
            name='job_type',
            field=models.CharField(max_length=50, choices=[(b'Buyer', b'Buyer'), (b'Supplier', b'Supplier'), (b'Sales Order CSV', b'Sales Order CSV'), (b'Shipment Sales Order CSV', b'Shipment Sales Order CSV'), (b'SKU Map CSV', b'SKU Map CSV'), (b'Company Map CSV', b'Company Map CSV'), (b'Catalog CSV', b'Catalog CSV'), (b'Catalog Bulk CSV', b'Catalog Bulk CSV'), (b'Product CSV', b'Product CSV'), (b'Shipment Dispatch CSV', b'Shipment Dispatch CSV')]),
        ),
    ]
