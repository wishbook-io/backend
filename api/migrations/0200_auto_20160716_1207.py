# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0199_auto_20160716_1143'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='skumap',
            unique_together=set([('app_instance', 'external_sku')]),
        ),
    ]
