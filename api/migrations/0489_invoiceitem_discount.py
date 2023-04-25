# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0488_auto_20171130_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='discount',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
