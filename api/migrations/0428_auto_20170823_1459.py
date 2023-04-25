# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0427_auto_20170823_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyrating',
            name='buyer_score',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=4, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='companyrating',
            name='seller_score',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=4, decimal_places=2, blank=True),
        ),
    ]
