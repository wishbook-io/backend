# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0159_auto_20160525_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='sms_buyers_on_overdue',
            field=models.BooleanField(default=True),
        ),
    ]
