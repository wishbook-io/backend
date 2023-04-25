# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0433_jobs_error_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='exception_details',
            field=models.TextField(null=True, blank=True),
        ),
    ]
