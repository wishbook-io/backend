# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0342_auto_20170518_1037'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='push_user',
            index_together=set([('buying_company', 'selling_company'), ('selling_company', 'user', 'selection'), ('buying_company', 'push', 'user'), ('id', 'buying_company'), ('user', 'selection'), ('selling_company', 'catalog', 'push'), ('buying_company', 'selection', 'push'), ('catalog', 'selling_company'), ('user', 'catalog'), ('selling_company', 'user', 'catalog'), ('push', 'selling_company'), ('buying_company', 'catalog', 'push')]),
        ),
    ]
