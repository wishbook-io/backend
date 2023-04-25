# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0212_remove_product_catalog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='catalogs',
            new_name='catalog',
        ),
    ]
