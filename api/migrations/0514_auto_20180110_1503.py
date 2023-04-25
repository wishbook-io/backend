# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0513_auto_20180110_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='cod_verified',
        ),
        migrations.AddField(
            model_name='company',
            name='location_verified',
            field=models.BooleanField(default=False),
        ),
    ]
