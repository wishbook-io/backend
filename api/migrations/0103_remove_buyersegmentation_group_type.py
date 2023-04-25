# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0102_grouptype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyersegmentation',
            name='group_type',
        ),
    ]
