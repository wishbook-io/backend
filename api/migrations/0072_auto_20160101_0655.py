# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0071_push_user_product_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='fix_amount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='percentage_amount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
    ]
