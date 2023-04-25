# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0336_usersendnotification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usersendnotification',
            unique_together=set([('user', 'created_at')]),
        ),
    ]
