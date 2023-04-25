# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0214_auto_20160720_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catalog',
            name='category',
        ),
    ]
