# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0151_auto_20160520_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='customer_status',
            field=models.CharField(default=b'pending', max_length=20, choices=[(b'Draft', b'Draft'), (b'Placed', b'Placed'), (b'Paid', b'Paid'), (b'Payment Confirmed', b'Payment Confirmed'), (b'Cancelled', b'Cancelled')]),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Draft', max_length=20, null=True, choices=[(b'Pending', b'Pending'), (b'Accepted', b'Accepted'), (b'Dispatched', b'Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled')]),
        ),
    ]
