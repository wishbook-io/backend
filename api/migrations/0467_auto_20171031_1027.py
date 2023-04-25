# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0466_auto_20171017_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='broker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotion',
            name='manufacturer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotion',
            name='online_retailer_reseller',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotion',
            name='retailer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotion',
            name='wholesaler_distributor',
            field=models.BooleanField(default=False),
        ),
    ]
