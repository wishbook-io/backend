# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0217_auto_20160721_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appinstance',
            name='user',
        ),
    ]
