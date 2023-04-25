# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0215_remove_catalog_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catalog',
            old_name='categories',
            new_name='category',
        ),
    ]
