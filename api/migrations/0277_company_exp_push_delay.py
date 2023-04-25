# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0276_buyer_preferred_logistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='exp_push_delay',
            field=models.IntegerField(default=0),
        ),
    ]
