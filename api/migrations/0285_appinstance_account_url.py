# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0284_auto_20170123_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='appinstance',
            name='account_url',
            field=models.TextField(null=True, blank=True),
        ),
    ]
