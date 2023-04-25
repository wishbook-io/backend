# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0315_auto_20170325_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
    ]
