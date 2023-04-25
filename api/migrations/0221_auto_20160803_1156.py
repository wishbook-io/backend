# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0220_push_single_company_push'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push',
            name='buyer_segmentation',
            field=models.ForeignKey(related_name='push_buyer_segmentation', default=None, blank=True, to='api.BuyerSegmentation', null=True),
        ),
    ]
