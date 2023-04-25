# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0197_auto_20160716_1141'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skumap',
            old_name='sku',
            new_name='product',
        ),
    ]
