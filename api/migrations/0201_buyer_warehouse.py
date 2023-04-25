# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0200_auto_20160716_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='warehouse',
            field=models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True),
        ),
    ]
