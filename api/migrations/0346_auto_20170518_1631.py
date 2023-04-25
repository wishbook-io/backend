# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0345_auto_20170518_1624'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='catalog',
            index_together=set([('company', 'id'), ('company', 'id', 'brand'), ('company', 'brand')]),
        ),
        migrations.AlterIndexTogether(
            name='product',
            index_together=set([('id', 'catalog')]),
        ),
        migrations.AlterIndexTogether(
            name='productlike',
            index_together=set([('user', 'product')]),
        ),
        migrations.AlterIndexTogether(
            name='salesorder',
            index_together=set([('user', 'company')]),
        ),
        migrations.AlterIndexTogether(
            name='salesorderitem',
            index_together=set([('id', 'sales_order')]),
        ),
    ]
