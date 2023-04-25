# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0260_auto_20161014_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='rate',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
