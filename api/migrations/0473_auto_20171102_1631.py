# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0472_auto_20171102_1627'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerageOrderFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='BrokeragePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('payment_date', models.DateField()),
                ('payment_method', models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other'), (b'Wishbook Credit', b'Wishbook Credit')])),
                ('payment_details', models.TextField(null=True, blank=True)),
                ('company', models.ForeignKey(related_name='brokeragepaymentcompanies', to='api.Company')),
                ('selling_company', models.ForeignKey(related_name='brokeragepaymentsellingcompanies', to='api.Company')),
            ],
        ),
        migrations.AddField(
            model_name='brokerageorderfee',
            name='brokerage_payment',
            field=models.ForeignKey(to='api.BrokeragePayment'),
        ),
        migrations.AddField(
            model_name='brokerageorderfee',
            name='order',
            field=models.ForeignKey(to='api.SalesOrder'),
        ),
        migrations.AddField(
            model_name='brokerageorderfee',
            name='selling_company',
            field=models.ForeignKey(to='api.Company'),
        ),
    ]
