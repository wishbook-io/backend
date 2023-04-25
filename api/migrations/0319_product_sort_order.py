# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0318_auto_20170327_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
