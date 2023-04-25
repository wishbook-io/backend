# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0509_auto_20180105_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='location_address',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='location_city',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='location_state',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
