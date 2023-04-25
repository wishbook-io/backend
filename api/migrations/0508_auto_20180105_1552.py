# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0507_auto_20171230_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='location_address',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='location_city',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='location_state',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
