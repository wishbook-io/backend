# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0128_auto_20160506_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Pending', max_length=20, null=True, choices=[(b'Pending', b'Pending'), (b'ordered', b'Ordered'), (b'dispatched', b'Dispatched'), (b'delivered', b'Delivered'), (b'cancelled', b'Cancelled')]),
        ),
    ]
