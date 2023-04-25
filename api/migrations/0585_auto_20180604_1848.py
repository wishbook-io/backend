# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0584_viewfollower'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(max_length=50, null=True, blank=True)),
                ('payment_details', models.TextField(null=True, blank=True)),
                ('payment_date', models.DateField(null=True, blank=True)),
                ('brokerage_fees', models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2)),
                ('preffered_shipping_provider', models.CharField(default=b'Buyer Suggested', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')])),
                ('buyer_preferred_logistics', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('shipping_charges', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True)),
                ('order_type', models.CharField(default=b'Prepaid', max_length=20, choices=[(b'Prepaid', b'Prepaid'), (b'Credit', b'Credit')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('payment_method', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other'), (b'Wishbook Credit', b'Wishbook Credit'), (b'COD', b'COD')])),
                ('total_qty', models.IntegerField(default=0)),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('paid_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('pending_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('payment_status', models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Partially Paid', b'Partially Paid'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')])),
                ('taxes', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('total_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('seller_discount', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True)),
                ('created_type', models.CharField(default=b'Cart', max_length=20, null=True, blank=True, choices=[(b'Cart', b'Cart'), (b'Order', b'Order')])),
                ('cart_status', models.CharField(default=b'Created', max_length=20, null=True, blank=True, choices=[(b'Created', b'Created'), (b'Converted', b'Converted')])),
                ('broker_company', models.ForeignKey(related_name='cart_broker_company', default=None, blank=True, to='api.Company', null=True)),
                ('buying_company', models.ForeignKey(related_name='cart_buying_company', to='api.Company')),
                ('ship_to', models.ForeignKey(default=None, blank=True, to='api.Address', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('rate', models.DecimalField(null=True, max_digits=19, decimal_places=2)),
                ('packing_type', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Box', b'Box'), (b'Naked', b'Naked')])),
                ('note', models.TextField(null=True, blank=True)),
                ('tax_value_1', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('tax_value_2', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('total_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('discount', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True)),
                ('is_full_catalog', models.BooleanField(default=False)),
                ('cart', models.ForeignKey(related_name='items', default=None, to='api.Cart')),
                ('product', models.ForeignKey(to='api.Product', on_delete=django.db.models.deletion.PROTECT)),
                ('selling_company', models.ForeignKey(related_name='cartitem_selling_company', to='api.Company')),
                ('tax_class_1', models.ForeignKey(related_name='cartitem_tax_class_1', default=None, blank=True, to='api.TaxClass', null=True)),
                ('tax_class_2', models.ForeignKey(related_name='cartitem_tax_class_2', default=None, blank=True, to='api.TaxClass', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other'), (b'Wishbook Credit', b'Wishbook Credit'), (b'COD', b'COD')])),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('status', models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Partially Paid', b'Partially Paid'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')])),
                ('payment_details', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cart', models.ForeignKey(to='api.Cart')),
                ('user', models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='salesorder',
            name='amount',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='seller_extra_discount_percentage',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='amount',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='seller_extra_discount_percentage',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorderitem',
            name='is_full_catalog',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='salesorderitem',
            name='product',
            field=models.ForeignKey(to='api.Product', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='cart',
            field=models.ForeignKey(default=None, blank=True, to='api.Cart', null=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='cart',
            field=models.ForeignKey(default=None, blank=True, to='api.Cart', null=True),
        ),
    ]
