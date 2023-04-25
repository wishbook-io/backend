# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0278_auto_20161226_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='exp_desp_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
