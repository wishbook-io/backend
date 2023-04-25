# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0346_auto_20170518_1631'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='barcode',
            index_together=set([('warehouse', 'product')]),
        ),
        migrations.AlterIndexTogether(
            name='buyer',
            index_together=set([('selling_company', 'group_type'), ('selling_company', 'buying_company', 'group_type'), ('selling_company', 'buying_company')]),
        ),
        migrations.AlterIndexTogether(
            name='catalogselectionstatus',
            index_together=set([('company', 'selection'), ('company', 'catalog')]),
        ),
        migrations.AlterIndexTogether(
            name='invitee',
            index_together=set([('invite', 'country')]),
        ),
        migrations.AlterIndexTogether(
            name='productstatus',
            index_together=set([('company', 'product')]),
        ),
        migrations.AlterIndexTogether(
            name='push',
            index_together=set([('company', 'buyer_segmentation')]),
        ),
        migrations.AlterIndexTogether(
            name='selection',
            index_together=set([('user', 'id')]),
        ),
        migrations.AlterIndexTogether(
            name='skumap',
            index_together=set([('product', 'app_instance')]),
        ),
        migrations.AlterIndexTogether(
            name='stock',
            index_together=set([('warehouse', 'product')]),
        ),
        migrations.AlterIndexTogether(
            name='userprofile',
            index_together=set([('user', 'country')]),
        ),
    ]
