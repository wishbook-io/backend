# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0490_meeting_buyer_name_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='companycatalogview',
            name='clicks',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
