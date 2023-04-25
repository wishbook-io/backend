# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0287_remove_salesorder_backorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesorder',
            name='backorder_id',
        ),
    ]
