# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0114_auto_20160325_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitee',
            name='group_type',
        ),
    ]
