# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0351_userprofile_first_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionalnotification',
            name='broker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='manufacturer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='online_retailer_reseller',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='retailer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='wholesaler_distributor',
            field=models.BooleanField(default=False),
        ),
    ]
