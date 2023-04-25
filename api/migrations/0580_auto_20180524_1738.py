# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0579_auto_20180523_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketing',
            name='append_deeplink_insms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='marketing',
            name='company_number_type_broker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='marketing',
            name='company_number_type_online_retailer_reseller',
            field=models.BooleanField(default=False),
        ),
    ]
