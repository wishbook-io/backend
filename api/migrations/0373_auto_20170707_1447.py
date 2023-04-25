# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0372_auto_20170707_1128'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='push_user_product',
            index_together=set([]),
        ),
    ]
