# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0211_product_catalogs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='catalog',
        ),
    ]
