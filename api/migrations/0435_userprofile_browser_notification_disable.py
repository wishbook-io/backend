# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0434_jobs_exception_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='browser_notification_disable',
            field=models.BooleanField(default=False),
        ),
    ]
