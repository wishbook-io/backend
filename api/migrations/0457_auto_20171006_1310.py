# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0456_paymentmethod_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companybuyergroup',
            name='price_list',
            field=models.ForeignKey(related_name='pricelist_buyer_group', default=None, blank=True, to='api.CompanyPriceList', null=True),
        ),
    ]
