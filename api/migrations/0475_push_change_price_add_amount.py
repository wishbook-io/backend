# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0474_auto_20171110_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='change_price_add_amount',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
