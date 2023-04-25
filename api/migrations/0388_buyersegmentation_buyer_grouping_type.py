# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0387_auto_20170718_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersegmentation',
            name='buyer_grouping_type',
            field=models.CharField(default=b'Location Wise', max_length=50, choices=[(b'Location Wise', b'Location Wise'), (b'Custom', b'Custom')]),
        ),
    ]
