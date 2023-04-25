# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0103_remove_buyersegmentation_group_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='group_type',
        ),
    ]
