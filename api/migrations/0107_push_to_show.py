# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0106_buyersegmentation_group_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='to_show',
            field=models.CharField(default=b'yes', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
