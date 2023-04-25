# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0555_auto_20180419_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='campaign_name',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
    ]
