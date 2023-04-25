# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0301_auto_20170320_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishbookInvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('item_type', models.CharField(max_length=200)),
                ('qty', models.PositiveIntegerField(null=True, blank=True)),
                ('rate', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('invoice', models.ForeignKey(default=None, blank=True, to='api.WishbookInvoice', null=True)),
            ],
        ),
    ]
