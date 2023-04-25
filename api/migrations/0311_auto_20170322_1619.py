# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0310_auto_20170322_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='status',
            field=models.CharField(max_length=50, choices=[(b'buyer_registrationpending', b'Buyer Registration Pending'), (b'supplier_registrationpending', b'Supplier Registration Pending'), (b'buyer_pending', b'Buyer Pending'), (b'supplier_pending', b'Supplier Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected'), (b'Pending References', b'Pending References'), (b'Transferred', b'Transferred'), (b'References Filled', b'References Filled')]),
        ),
    ]
