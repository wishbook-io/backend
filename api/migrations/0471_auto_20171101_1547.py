# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0470_auto_20171101_1533'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='skumap',
            index_together=set([]),
        ),
    ]
