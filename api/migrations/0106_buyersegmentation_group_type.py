# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0105_buyer_group_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersegmentation',
            name='group_type',
            field=models.ManyToManyField(to='api.GroupType'),
        ),
    ]
