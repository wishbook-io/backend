# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0449_auto_20171004_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='default_catalog_lifetime',
            field=models.IntegerField(default=60),
        ),
    ]
