# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0187_auto_20160711_1238'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appinstance',
            unique_together=set([('app', 'company')]),
        ),
    ]
