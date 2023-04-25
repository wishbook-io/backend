# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0183_dispatch_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorderitem',
            name='pending_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
