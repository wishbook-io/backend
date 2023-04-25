# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0405_auto_20170802_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='status',
            field=models.CharField(default=b'Invoiced', max_length=20, null=True, choices=[(b'Invoiced', b'Invoiced'), (b'Dispatched', b'Dispatched')]),
        ),
    ]
