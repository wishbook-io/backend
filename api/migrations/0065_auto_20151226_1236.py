# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_auto_20151226_1224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='push_user_product',
            name='catalog',
        ),
        migrations.RemoveField(
            model_name='push_user_product',
            name='selection',
        ),
    ]
