# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0280_auto_20161226_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyersegmentation',
            name='category',
            field=models.ManyToManyField(to='api.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='buyersegmentation',
            name='city',
            field=models.ManyToManyField(to='api.City', blank=True),
        ),
    ]
