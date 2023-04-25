# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20151202_0512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='percentage_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2),
        ),
    ]
