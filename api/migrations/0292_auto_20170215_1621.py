# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0291_cronhistry'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CronHistry',
            new_name='CronHistory',
        ),
    ]
