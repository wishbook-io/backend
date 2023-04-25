# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0165_promotionalnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='sell_full_catalog',
            field=models.BooleanField(default=False),
        ),
    ]
