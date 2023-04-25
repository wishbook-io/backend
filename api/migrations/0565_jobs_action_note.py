# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0564_salesorderauditlogentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='action_note',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
