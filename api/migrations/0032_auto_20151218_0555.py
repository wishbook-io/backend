# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_auto_20151218_0544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='category',
            field=models.ManyToManyField(to='api.Category', blank=True),
        ),
    ]
