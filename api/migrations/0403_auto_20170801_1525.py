# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0402_auto_20170801_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='rate',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='total_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
