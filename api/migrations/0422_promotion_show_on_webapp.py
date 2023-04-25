# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0421_auto_20170821_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='show_on_webapp',
            field=models.BooleanField(default=False),
        ),
    ]
