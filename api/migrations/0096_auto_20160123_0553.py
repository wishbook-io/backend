# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0095_auto_20160121_0704'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cataloglist',
            unique_together=set([('name', 'user')]),
        ),
    ]
