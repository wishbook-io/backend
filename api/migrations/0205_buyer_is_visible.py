# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0204_remove_buyer_is_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='is_visible',
            field=models.BooleanField(default=False),
        ),
    ]
