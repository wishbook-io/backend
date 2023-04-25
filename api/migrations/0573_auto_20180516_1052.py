# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0572_auto_20180514_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogenquiry',
            name='status',
            field=models.CharField(default=b'Created', max_length=30, choices=[(b'Created', b'Created'), (b'Resolved', b'Resolved')]),
        ),
    ]
