# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0400_auto_20170801_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxclass',
            name='percentage',
            field=models.DecimalField(max_digits=19, decimal_places=2),
        ),
    ]
