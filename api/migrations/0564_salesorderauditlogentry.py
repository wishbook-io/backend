# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
from decimal import Decimal
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0563_imagetestauditlogentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrderAuditLogEntry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('order_number', models.CharField(max_length=50, null=True, blank=True)),
                ('seller_ref', models.CharField(max_length=50, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField(auto_now=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('processing_status', models.CharField(default=b'Pending', max_length=20, null=True, choices=[(b'Cart', b'Cart'), (b'Pending', b'Pending'), (b'Draft', b'Draft'), (b'Accepted', b'Accepted'), (b'In Progress', b'In Progress'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled'), (b'Closed', b'Closed'), (b'Buyer Cancelled', b'Buyer Cancelled')])),
                ('customer_status', models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Draft', b'Draft'), (b'Placed', b'Placed'), (b'Paid', b'Paid'), (b'Payment Confirmed', b'Payment Confirmed'), (b'Cancelled', b'Cancelled'), (b'pending', b'pending'), (b'finalized', b'finalized')])),
                ('sales_image', models.ImageField(null=True, upload_to=b'order', blank=True)),
                ('purchase_image', models.ImageField(null=True, upload_to=b'order', blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('tracking_details', models.TextField(null=True, blank=True)),
                ('supplier_cancel', models.TextField(null=True, blank=True)),
                ('buyer_cancel', models.TextField(null=True, blank=True)),
                ('payment_details', models.TextField(null=True, blank=True)),
                ('payment_date', models.DateField(null=True, blank=True)),
                ('dispatch_date', models.DateField(null=True, blank=True)),
                ('brokerage_fees', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('sales_image_2', models.ImageField(null=True, upload_to=b'order', blank=True)),
                ('sales_image_3', models.ImageField(null=True, upload_to=b'order', blank=True)),
                ('sales_reference_id', models.IntegerField(null=True, blank=True)),
                ('purchase_reference_id', models.IntegerField(null=True, blank=True)),
                ('is_supplier_approved', models.BooleanField(default=True)),
                ('buying_company_name', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('preffered_shipping_provider', models.CharField(default=b'Buyer Suggested', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')])),
                ('buyer_preferred_logistics', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('shipping_charges', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True)),
                ('transaction_type', models.CharField(default=b'Marketplace', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')])),
                ('cancelled_by', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Buyer', b'Buyer'), (b'Seller', b'Seller')])),
                ('seller_cancellation_reason', models.CharField(default=None, max_length=30, null=True, blank=True, choices=[(b'Not In Stock', b'Not In Stock'), (b'Credit', b'Credit'), (b'Other', b'Other')])),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, editable=False, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')])),
                ('action_user', audit_log.models.fields.LastUserField(related_name='_salesorder_audit_log_entry', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('broker_company', models.ForeignKey(related_name='_auditlog_broker_company', default=None, blank=True, to='api.Company', null=True)),
                ('company', models.ForeignKey(related_name='_auditlog_buying_order', to='api.Company')),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='_auditlog_created_salesorders', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', audit_log.models.fields.LastUserField(related_name='_auditlog_modified_salesorders', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('seller_company', models.ForeignKey(related_name='_auditlog_selling_order', to='api.Company')),
                ('ship_to', models.ForeignKey(default=None, blank=True, to='api.Address', null=True)),
                ('tranferred_to', models.ForeignKey(related_name='_auditlog_tranferred_order', blank=True, to='api.SalesOrder', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('wb_coupon', models.ForeignKey(default=None, blank=True, to='api.WbCoupon', null=True)),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
        ),
    ]
