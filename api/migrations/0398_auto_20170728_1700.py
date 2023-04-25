# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0397_categorytaxclass'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_code_1',
            field=models.ForeignKey(related_name='tax_code_1', default=None, blank=True, to='api.TaxCode', null=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_code_2',
            field=models.ForeignKey(related_name='tax_code_2', default=None, blank=True, to='api.TaxCode', null=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_value_1',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_value_2',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
    ]
