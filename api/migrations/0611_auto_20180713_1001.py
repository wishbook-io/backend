# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0610_auto_20180712_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketing',
            name='categories',
            field=models.ManyToManyField(related_name='marketings', to='api.Category'),
        ),
        migrations.AddField(
            model_name='marketing',
            name='minimum_category_views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
