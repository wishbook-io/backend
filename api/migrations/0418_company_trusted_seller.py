# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0417_auto_20170818_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='trusted_seller',
            field=models.BooleanField(default=False),
        ),
    ]
