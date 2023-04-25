# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0311_auto_20170322_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
    ]
