# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0119_companynumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='traking_details',
            field=models.TextField(null=True, blank=True),
        ),
    ]
