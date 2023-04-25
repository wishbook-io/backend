# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0285_appinstance_account_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='backorder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='backorder_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
