# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0407_promotionalnotification_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='customer_status',
            field=models.CharField(default=b'Draft', max_length=20, choices=[(b'Pending', b'Pending'), (b'Draft', b'Draft'), (b'Placed', b'Placed'), (b'Paid', b'Paid'), (b'Payment Confirmed', b'Payment Confirmed'), (b'Cancelled', b'Cancelled'), (b'pending', b'pending'), (b'finalized', b'finalized')]),
        ),
    ]
