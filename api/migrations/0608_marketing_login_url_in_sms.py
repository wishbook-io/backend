# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0607_auto_20180709_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketing',
            name='login_url_in_sms',
            field=models.BooleanField(default=False),
        ),
    ]
