# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0295_companyproductflat_is_salable'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='public_price',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
    ]
