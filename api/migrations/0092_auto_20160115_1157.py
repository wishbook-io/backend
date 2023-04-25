# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0091_auto_20160115_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='supplier_status',
        ),
        migrations.AlterField(
            model_name='buyer',
            name='status',
            field=models.CharField(max_length=20, choices=[(b'registrationpending', b'Registration Pending'), (b'buyer_pending', b'Buyer Pending'), (b'supplier_pending', b'Supplier Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
    ]
