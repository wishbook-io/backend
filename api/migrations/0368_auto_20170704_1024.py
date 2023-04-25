# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0367_auto_20170703_1859'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='pushsellerprice',
            index_together=set([('push', 'selling_company'), ('push', 'selling_company', 'product')]),
        ),
    ]
