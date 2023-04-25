# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0556_promotion_campaign_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('wishbook_salesman', models.TextField(null=True, blank=True)),
                ('company_type', models.TextField(null=True, blank=True)),
                ('city', models.CharField(max_length=100, null=True, blank=True)),
                ('phone_number', models.CharField(max_length=13, null=True, blank=True)),
                ('last_login', models.DateTimeField(null=True, blank=True)),
                ('catalogs_uploaded', models.TextField(null=True, blank=True)),
                ('total_catalog_seller', models.IntegerField(null=True, blank=True)),
                ('total_enabled_catalog', models.IntegerField(null=True, blank=True)),
                ('last_catalog_upload_date', models.DateField(null=True, blank=True)),
                ('last_catalog_seller_date', models.DateField(null=True, blank=True)),
                ('last_catalog_or_seller_name', models.CharField(max_length=250, null=True, blank=True)),
                ('total_enquiry_received', models.IntegerField(null=True, blank=True)),
                ('total_enquiry_converted', models.IntegerField(null=True, blank=True)),
                ('total_enquiry_pending', models.IntegerField(null=True, blank=True)),
                ('total_enquiry_values', models.IntegerField(null=True, blank=True)),
                ('handling_time', models.DurationField(null=True, blank=True)),
                ('total_order_values', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('total_pending_order_values', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('total_prepaid_order_values', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('total_prepaid_cancelled_order_values', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('avg_dispatch_time', models.DurationField(null=True, blank=True)),
                ('company', models.OneToOneField(to='api.Company')),
            ],
        ),
    ]
