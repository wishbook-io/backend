# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0253_invoice_invoiceitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField()),
                ('balance_amount', models.PositiveIntegerField()),
                ('expire_date', models.DateField()),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField()),
                ('credit', models.ForeignKey(to='api.Credit')),
                ('invoice', models.ForeignKey(to='api.Invoice')),
            ],
        ),
    ]
