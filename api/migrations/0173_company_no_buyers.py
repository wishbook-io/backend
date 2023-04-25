# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0172_auto_20160616_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='no_buyers',
            field=models.BooleanField(default=False),
        ),
    ]
