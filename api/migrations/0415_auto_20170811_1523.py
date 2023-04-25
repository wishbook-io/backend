# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0414_auto_20170810_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(default=b'Invoiced', max_length=20, null=True, choices=[(b'Invoiced', b'Invoiced'), (b'Dispatched', b'Dispatched'), (b'Cancelled', b'Cancelled')]),
        ),
    ]
