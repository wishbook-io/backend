# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0074_auto_20160101_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='picasa_id',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='picasa_url',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
