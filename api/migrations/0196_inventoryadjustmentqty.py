# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0195_inventoryadjustment'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryAdjustmentQty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=0)),
                ('adjustment_type', models.CharField(max_length=20, choices=[(b'Add', b'Add'), (b'Remove', b'Remove'), (b'Transfer', b'Transfer')])),
                ('inventory_adjustment', models.ForeignKey(to='api.InventoryAdjustment')),
                ('product', models.ForeignKey(to='api.Product')),
                ('to_warehouse', models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True)),
            ],
        ),
    ]
