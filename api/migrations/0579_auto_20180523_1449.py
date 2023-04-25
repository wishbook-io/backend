# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0578_auto_20180522_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='approximate_order',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='approximate_order',
            field=models.BooleanField(default=False),
        ),
    ]
