# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0139_auto_20160518_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='cash_discount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='buyer',
            name='discount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='buyer',
            name='payment_duration',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
    ]
