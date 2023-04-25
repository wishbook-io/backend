# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0358_jobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='status',
            field=models.CharField(max_length=50, choices=[(b'Scheduled', b'Scheduled'), (b'In Progress', b'In Progress'), (b'Complete', b'Complete'), (b'Complete With Errors', b'Complete With Errors')]),
        ),
    ]
