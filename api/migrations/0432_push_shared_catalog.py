# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0431_auto_20170831_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='shared_catalog',
            field=models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
