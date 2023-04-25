# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0469_auto_20171101_1105'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='skumap',
            unique_together=set([('app_instance', 'product', 'catalog')]),
        ),
    ]
