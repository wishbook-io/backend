# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0261_auto_20161018_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='credit',
            name='balance_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='balance_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='billed_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='discount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoicecredit',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='invoicepayment',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
