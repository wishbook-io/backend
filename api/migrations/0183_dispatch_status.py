# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0182_dispatch_dispatchitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispatch',
            name='status',
            field=models.CharField(default=b'Dispatched', max_length=20, choices=[(b'Dispatched', b'Dispatched'), (b'Delivered', b'Delivered'), (b'Canceled', b'Canceled'), (b'Closed', b'Closed')]),
        ),
    ]
