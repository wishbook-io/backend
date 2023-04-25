# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0382_stock_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Pending', max_length=20, null=True, choices=[(b'Pending', b'Pending'), (b'Accepted', b'Accepted'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled')]),
        ),
    ]
