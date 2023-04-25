# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0435_userprofile_browser_notification_disable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='push',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
