# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0356_auto_20170617_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='wishbook_salesman',
            field=models.TextField(null=True, blank=True),
        ),
    ]
