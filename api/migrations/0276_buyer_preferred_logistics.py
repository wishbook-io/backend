# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0275_logistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='preferred_logistics',
            field=models.ForeignKey(default=None, blank=True, to='api.Logistics', null=True),
        ),
    ]
