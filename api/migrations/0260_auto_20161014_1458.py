# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0259_auto_20161014_1457'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='smstransaction',
            unique_together=set([('created_at', 'provider')]),
        ),
    ]
