# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0531_auto_20180227_1134'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('discount_type', models.CharField(max_length=20, choices=[(b'Public', b'Public'), (b'Private', b'Private')])),
                ('all_brands', models.BooleanField(default=False)),
                ('cash_discount', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('credit_discount', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('selling_company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountRuleBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brand', models.ForeignKey(to='api.Brand')),
                ('discount_rule', models.ForeignKey(to='api.DiscountRule')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountRuleBuyerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('buyer_group', models.ForeignKey(to='api.BuyerSegmentation')),
                ('discount_rule', models.ForeignKey(to='api.DiscountRule')),
            ],
        ),
    ]
