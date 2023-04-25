# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0612_auto_20180716_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='uninstall_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
