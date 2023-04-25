# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0504_auto_20171221_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='cash_discount',
            field=models.DecimalField(default=None, null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='discount',
            field=models.DecimalField(default=None, null=True, max_digits=10, decimal_places=2, blank=True),
        ),
    ]
