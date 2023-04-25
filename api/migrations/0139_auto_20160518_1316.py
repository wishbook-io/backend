# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0138_unregisteredphonealias'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyBuyerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_duration', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('discount', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('cash_discount', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('buyer_type', models.ForeignKey(to='api.GroupType')),
                ('company', models.ForeignKey(related_name='company_buyer_group', to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyPriceList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number_pricelists', models.CharField(max_length=10)),
                ('pricelist2_multiplier', models.CharField(max_length=10)),
                ('company', models.ForeignKey(related_name='pricelist', to='api.Company')),
            ],
        ),
        migrations.AddField(
            model_name='companybuyergroup',
            name='price_list',
            field=models.ForeignKey(related_name='pricelist_buyer_group', to='api.CompanyPriceList'),
        ),
    ]
