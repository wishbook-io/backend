# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_auto_20151223_0712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagetest',
            name='image_optional',
        ),
    ]
