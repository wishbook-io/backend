# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import api.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20151218_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='category',
            field=models.ManyToManyField(default=api.models.allCategories, to='api.Category', blank=True),
        ),
    ]
