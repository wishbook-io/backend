# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_auto_20151225_0705'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catalog',
            old_name='image',
            new_name='thumbnail',
        ),
        migrations.RenameField(
            model_name='catalog',
            old_name='image_ppoi',
            new_name='thumbnail_ppoi',
        ),
    ]
