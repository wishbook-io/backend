# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0521_updatenotification_app_version_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotionalnotification',
            name='category',
        ),
    ]
