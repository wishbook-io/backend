# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0141_auto_20160518_1655'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companyphonealias',
            unique_together=set([('country', 'alias_number')]),
        ),
    ]
