# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0569_auto_20180503_1126'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiSalesorderauditlogentry',
            fields=[
                ('id', models.IntegerField()),
                ('order_number', models.CharField(max_length=50, null=True, blank=True)),
                ('seller_ref', models.CharField(max_length=50, null=True, blank=True)),
                ('created_at', models.DateTimeField()),
                ('date', models.DateField()),
                ('time', models.DateTimeField()),
                ('processing_status', models.CharField(max_length=20, null=True, blank=True)),
                ('customer_status', models.CharField(max_length=20)),
                ('sales_image', models.CharField(max_length=100, null=True, blank=True)),
                ('purchase_image', models.CharField(max_length=100, null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('tracking_details', models.TextField(null=True, blank=True)),
                ('supplier_cancel', models.TextField(null=True, blank=True)),
                ('buyer_cancel', models.TextField(null=True, blank=True)),
                ('payment_details', models.TextField(null=True, blank=True)),
                ('payment_date', models.DateField(null=True, blank=True)),
                ('dispatch_date', models.DateField(null=True, blank=True)),
                ('brokerage_fees', models.DecimalField(max_digits=19, decimal_places=2)),
                ('sales_image_2', models.CharField(max_length=100, null=True, blank=True)),
                ('sales_image_3', models.CharField(max_length=100, null=True, blank=True)),
                ('sales_reference_id', models.IntegerField(null=True, blank=True)),
                ('purchase_reference_id', models.IntegerField(null=True, blank=True)),
                ('is_supplier_approved', models.IntegerField()),
                ('buying_company_name', models.CharField(max_length=250, null=True, blank=True)),
                ('preffered_shipping_provider', models.CharField(max_length=20, null=True, blank=True)),
                ('buyer_preferred_logistics', models.CharField(max_length=250, null=True, blank=True)),
                ('shipping_charges', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('transaction_type', models.CharField(max_length=50)),
                ('cancelled_by', models.CharField(max_length=20, null=True, blank=True)),
                ('seller_cancellation_reason', models.CharField(max_length=30, null=True, blank=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField()),
                ('action_type', models.CharField(max_length=1)),
                ('order_type', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Sales Order Log Entry',
                'db_table': 'api_salesorderauditlogentry',
                'managed': False,
                'verbose_name_plural': 'Sales Order Log Entry',
            },
        ),
        migrations.AlterField(
            model_name='jobs',
            name='job_type',
            field=models.CharField(max_length=50, choices=[(b'Buyer', b'Buyer'), (b'Supplier', b'Supplier'), (b'Sales Order CSV', b'Sales Order CSV'), (b'Shipment Sales Order CSV', b'Shipment Sales Order CSV'), (b'SKU Map CSV', b'SKU Map CSV'), (b'Company Map CSV', b'Company Map CSV'), (b'Catalog CSV', b'Catalog CSV'), (b'Product CSV', b'Product CSV'), (b'Shipment Dispatch CSV', b'Shipment Dispatch CSV')]),
        ),
    ]
