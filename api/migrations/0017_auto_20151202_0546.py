# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20151202_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='fabric',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='work',
            field=models.TextField(null=True, blank=True),
        ),
    ]
