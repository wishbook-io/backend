# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0176_auto_20160627_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
