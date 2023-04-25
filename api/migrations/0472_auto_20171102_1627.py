# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0471_auto_20171101_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='brokerage_fees',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='brokerage_fees',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
    ]
