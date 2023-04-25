# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0508_auto_20180105_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='location_city',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='location_state',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
