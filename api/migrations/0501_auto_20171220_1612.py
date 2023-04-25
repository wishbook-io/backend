# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0500_catalogseller'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogseller',
            name='buyer_segmentation',
            field=models.ForeignKey(default=None, blank=True, to='api.BuyerSegmentation', null=True),
        ),
        migrations.AddField(
            model_name='catalogseller',
            name='expiry_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
