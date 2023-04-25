# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0343_auto_20170518_1115'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='companyproductflat',
            index_together=set([('product', 'selection', 'buying_company'), ('product', 'buying_company', 'selling_company', 'selection'), ('product', 'buying_company', 'selling_company', 'catalog'), ('buying_company', 'selling_company', 'catalog'), ('product', 'catalog', 'buying_company'), ('buying_company', 'selling_company', 'selection'), ('buying_company', 'selection'), ('buying_company', 'catalog')]),
        ),
        migrations.AlterIndexTogether(
            name='push_user_product',
            index_together=set([('push', 'user', 'selection'), ('id', 'buying_company'), ('push', 'user', 'catalog'), ('user', 'product'), ('push', 'selling_company', 'is_viewed'), ('user', 'selling_company'), ('buying_company', 'product')]),
        ),
    ]
