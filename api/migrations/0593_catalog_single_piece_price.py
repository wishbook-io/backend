# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0592_auto_20180619_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='single_piece_price',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
