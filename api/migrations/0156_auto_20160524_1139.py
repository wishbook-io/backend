# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0155_auto_20160521_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push',
            name='status',
            field=models.CharField(default=b'In Progress', max_length=20, choices=[(b'Schedule', b'Schedule'), (b'Delivered', b'Delivered'), (b'Pending', b'Pending'), (b'In Progress', b'In Progress')]),
        ),
    ]
