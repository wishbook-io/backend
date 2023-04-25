# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20151106_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='picasa_id',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalog',
            name='picasa_url',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
