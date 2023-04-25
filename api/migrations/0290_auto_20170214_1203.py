# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0289_salesorder_backorders'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_profile_set',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_profile_set',
            field=models.BooleanField(default=True),
        ),
    ]
