# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0286_auto_20170128_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesorder',
            name='backorder',
        ),
    ]
