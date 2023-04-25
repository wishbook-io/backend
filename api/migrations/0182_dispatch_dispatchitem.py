# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0181_catalogselectionstatus_productstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dispatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('dispatch_details', models.TextField(null=True, blank=True)),
                ('sales_order', models.ForeignKey(related_name='dispatch', default=None, to='api.SalesOrder')),
            ],
        ),
        migrations.CreateModel(
            name='DispatchItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('sales_order_item', models.ForeignKey(related_name='dispatch_item', default=None, to='api.SalesOrderItem')),
            ],
        ),
    ]
