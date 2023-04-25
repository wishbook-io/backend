# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0148_auto_20160519_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Draft', max_length=20, null=True, choices=[(b'Draft', b'Draft'), (b'Placed', b'Placed'), (b'dispatched', b'Dispatched'), (b'delivered', b'Delivered'), (b'cancelled', b'Cancelled')]),
        ),
    ]
