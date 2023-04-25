# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0539_sellerpolicy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountrule',
            name='brands',
            field=models.ManyToManyField(to='api.Brand', blank=True),
        ),
        migrations.AlterField(
            model_name='discountrule',
            name='buyer_segmentations',
            field=models.ManyToManyField(to='api.BuyerSegmentation', blank=True),
        ),
    ]
