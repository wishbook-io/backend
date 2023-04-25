# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_product_image_small_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catalog',
            name='category',
        ),
        migrations.AddField(
            model_name='catalog',
            name='category',
            field=models.ManyToManyField(related_name='categories', to='api.Category'),
        ),
    ]
