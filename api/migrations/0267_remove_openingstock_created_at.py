# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0266_auto_20161027_1241'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='openingstock',
            name='created_at',
        ),
    ]
