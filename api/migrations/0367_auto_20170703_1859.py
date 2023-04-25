# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0366_promotion'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pushsellerprice',
            unique_together=set([('push', 'selling_company', 'product')]),
        ),
    ]
