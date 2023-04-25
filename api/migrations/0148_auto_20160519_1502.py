# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0147_salesorder_payment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='customer_status',
            field=models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'finalized', b'Finalized'), (b'Paid', b'Paid'), (b'Payment_Confirmed', b'Payment Confirmed'), (b'Cancelled', b'Cancelled')]),
        ),
    ]
