# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0338_auto_20170503_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='paid_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='pending_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
