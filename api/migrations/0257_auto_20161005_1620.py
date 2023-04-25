# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0256_auto_20161005_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='amount',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(default=None, blank=True, to='api.Invoice', null=True),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='qty',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='rate',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
