# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0465_auto_20171016_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='buyer_preferred_logistics',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='preffered_shipping_provider',
            field=models.CharField(default=b'WB Provided', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')]),
        ),
        migrations.AddField(
            model_name='invoice',
            name='shipping_charges',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='preffered_shipping_provider',
            field=models.CharField(default=b'WB Provided', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')]),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='shipping_charges',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
