# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0479_auto_20171118_1033'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='warehousestock',
            unique_together=set([('warehouse', 'product')]),
        ),
        migrations.AlterIndexTogether(
            name='warehousestock',
            index_together=set([('warehouse', 'product')]),
        ),
    ]
