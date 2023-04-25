# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0512_auto_20180106_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='cod_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='cod_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pincodezone',
            name='cod_available',
            field=models.BooleanField(default=False),
        ),
    ]
