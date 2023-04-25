# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20151202_0546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'notfinalized', max_length=20, null=True, choices=[(b'notfinalized', b'Not Finalized'), (b'ordered', b'Ordered'), (b'dispatched', b'Dispatched'), (b'delivered', b'Delivered'), (b'canceled', b'Canceled')]),
        ),
    ]
