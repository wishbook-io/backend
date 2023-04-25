# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0177_catalog_is_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
