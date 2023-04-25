# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20151201_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='fix_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2),
        ),
        migrations.AddField(
            model_name='buyer',
            name='percentage_amount',
            field=models.DecimalField(null=True, max_digits=3, decimal_places=2),
        ),
    ]
