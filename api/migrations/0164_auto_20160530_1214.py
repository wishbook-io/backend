# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0163_auto_20160528_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='change_price_add',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='push',
            name='change_price_fix',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
