# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0420_auto_20170821_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='release_instrument',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'NEFT', b'NEFT')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='release_instrument_inumber',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='released_to_seller',
            field=models.BooleanField(default=False),
        ),
    ]
