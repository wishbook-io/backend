# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_auto_20151225_0704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catalog',
            old_name='images_ppoi',
            new_name='image_ppoi',
        ),
    ]
