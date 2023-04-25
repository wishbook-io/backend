# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0175_stock'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stock',
            unique_together=set([('warehouse', 'product')]),
        ),
    ]
