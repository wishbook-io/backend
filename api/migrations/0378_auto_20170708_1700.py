# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0377_buyersalesmen_buyers'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='buyersalesmen',
            unique_together=set([]),
        ),
    ]
