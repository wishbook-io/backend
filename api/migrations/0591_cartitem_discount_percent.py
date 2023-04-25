# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0590_auto_20180612_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='discount_percent',
            field=models.DecimalField(default=Decimal('0.00'), null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
