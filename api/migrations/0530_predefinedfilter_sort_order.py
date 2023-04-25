# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0529_auto_20180220_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='predefinedfilter',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
