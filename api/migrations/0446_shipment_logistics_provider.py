# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0445_auto_20171002_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='logistics_provider',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
