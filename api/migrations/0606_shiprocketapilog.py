# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0605_auto_20180709_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipRocketApiLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider_access_type', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'CREATE', b'CREATE'), (b'AWB', b'AWB'), (b'PICKUP', b'PICKUP')])),
                ('api_provider', models.CharField(default=b'ShipRocket', max_length=50, null=True, blank=True)),
                ('provider_order_id', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_shipment_id', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_label_url', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_manifest_url', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_invoice_url', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_api_response', models.TextField(null=True, blank=True)),
                ('provider_awb_number', models.CharField(max_length=50, null=True, blank=True)),
                ('provider_status', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'SUCCESS', b'SUCCESS'), (b'FAILED', b'FAIELD')])),
                ('wishbook_order_ids', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
    ]
