# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0267_remove_openingstock_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryadjustmentqty',
            name='inventory_adjustment',
            field=models.ForeignKey(blank=True, to='api.InventoryAdjustment', null=True),
        ),
    ]
