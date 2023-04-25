# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0388_buyersegmentation_buyer_grouping_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersegmentation',
            name='buyers',
            field=models.ManyToManyField(related_name='group_buyers', to='api.Company', blank=True),
        ),
    ]
