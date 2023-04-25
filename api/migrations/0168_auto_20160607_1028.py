# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0167_updateapp'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UpdateApp',
            new_name='UpdateNotification',
        ),
    ]
