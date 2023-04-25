# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0468_auto_20171031_1121'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='salesorderitem',
            unique_together=set([('sales_order', 'product', 'packing_type')]),
        ),
    ]
