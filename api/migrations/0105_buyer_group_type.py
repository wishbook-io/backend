# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0104_remove_buyer_group_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='group_type',
            field=models.ForeignKey(default=1, to='api.GroupType'),
            preserve_default=False,
        ),
    ]
