# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0432_push_shared_catalog'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='error_details',
            field=models.TextField(null=True, blank=True),
        ),
    ]
