# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0559_catalog_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerstatistic',
            name='enquiry_not_handled',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sellerstatistic',
            name='prepaid_order_cancellation_rate',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sellerstatistic',
            name='total_pending_order',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
