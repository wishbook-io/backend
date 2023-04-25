# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20151217_0517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image_small_thumbnail',
        ),
    ]
