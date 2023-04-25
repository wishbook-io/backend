# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0221_auto_20160803_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 6, 12, 50, 18, 322055), auto_now_add=True),
            preserve_default=False,
        ),
    ]
