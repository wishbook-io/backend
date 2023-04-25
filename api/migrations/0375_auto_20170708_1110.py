# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0374_auto_20170708_1104'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='buyersalesmen',
            unique_together=set([('buyer', 'salesman')]),
        ),
    ]
