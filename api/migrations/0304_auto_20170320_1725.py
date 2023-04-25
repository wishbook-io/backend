# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0303_auto_20170320_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishbookInvoiceCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('credit', models.ForeignKey(to='api.WishbookCredit')),
                ('invoice', models.ForeignKey(to='api.WishbookInvoice')),
            ],
        ),
        migrations.CreateModel(
            name='WishbookPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instrument', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('detail', models.CharField(max_length=200)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
