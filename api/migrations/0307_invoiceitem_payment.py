# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0306_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.IntegerField(default=0)),
                ('invoice', models.ForeignKey(to='api.Invoice')),
                ('order_item', models.ForeignKey(to='api.SalesOrderItem')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Other', b'Other')])),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('status', models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled')])),
                ('details', models.TextField(null=True, blank=True)),
                ('by_company', models.ForeignKey(related_name='payment_by', to='api.Company')),
                ('to_company', models.ForeignKey(related_name='payment_to', to='api.Company')),
            ],
        ),
    ]
