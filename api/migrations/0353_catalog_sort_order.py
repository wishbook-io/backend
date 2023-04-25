# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0352_auto_20170523_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
