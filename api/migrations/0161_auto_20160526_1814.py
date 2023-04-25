# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0160_company_sms_buyers_on_overdue'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='credit_limit',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='companybuyergroup',
            name='credit_limit',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
    ]
