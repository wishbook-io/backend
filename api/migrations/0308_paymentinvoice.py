# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0307_invoiceitem_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('transaction_reference', models.TextField(null=True, blank=True)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('invoice', models.ForeignKey(to='api.Invoice')),
            ],
        ),
    ]
