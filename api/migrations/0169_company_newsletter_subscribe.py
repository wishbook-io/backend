# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0168_auto_20160607_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='newsletter_subscribe',
            field=models.BooleanField(default=True),
        ),
    ]
