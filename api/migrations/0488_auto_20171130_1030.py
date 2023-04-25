# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0487_brand_total_catalog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cashback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('status', models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid')])),
                ('buyer', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='CashbackRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_type', models.CharField(max_length=50, choices=[(b'Online', b'Online'), (b'Offline', b'Offline'), (b'Credit', b'Credit')])),
                ('shipping_status', models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Dispatched', b'Dispatched'), (b'Delivered', b'Delivered'), (b'Canceled', b'Canceled')])),
                ('payment_status', models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')])),
                ('expire_date', models.DateField()),
                ('times_per_buyer', models.IntegerField(default=1)),
                ('seller', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.AddField(
            model_name='cashback',
            name='cashback_rule',
            field=models.ForeignKey(to='api.CashbackRule'),
        ),
        migrations.AddField(
            model_name='cashback',
            name='sales_order',
            field=models.ForeignKey(to='api.SalesOrder'),
        ),
    ]
