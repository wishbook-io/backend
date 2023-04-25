# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0506_promotionaltag'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='latitude',
            field=models.DecimalField(default=None, null=True, max_digits=10, decimal_places=7, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='longitude',
            field=models.DecimalField(default=None, null=True, max_digits=10, decimal_places=7, blank=True),
        ),
    ]
