# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0444_approvedcredit_loan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvedcredit',
            name='available_limit',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='approvedcredit',
            name='used_limit',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=19, decimal_places=2),
        ),
    ]
