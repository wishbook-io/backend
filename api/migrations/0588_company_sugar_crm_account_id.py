# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0587_auto_20180611_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='sugar_crm_account_id',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
