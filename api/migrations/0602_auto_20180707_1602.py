# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0601_companybankdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='dispatch_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='processing_status',
            field=models.CharField(default=b'Cart', max_length=50, null=True, blank=True, choices=[(b'Cart', b'Cart'), (b'Draft', b'Draft'), (b'COD Verification Pending', b'COD Verification Pending'), (b'Field Verification Pending', b'Field Verification Pending'), (b'Pending', b'Pending'), (b'Accepted', b'Accepted'), (b'In Progress', b'In Progress'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled'), (b'Closed', b'Closed'), (b'Buyer Cancelled', b'Buyer Cancelled')]),
        ),
    ]
