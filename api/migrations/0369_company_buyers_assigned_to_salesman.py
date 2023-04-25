# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0368_auto_20170704_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='buyers_assigned_to_salesman',
            field=models.BooleanField(default=False),
        ),
    ]
