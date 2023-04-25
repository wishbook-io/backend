# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0046_auto_20151224_1059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catalog',
            old_name='thumbnail',
            new_name='image',
        ),
    ]
