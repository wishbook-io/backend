# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0378_auto_20170708_1700'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyersalesmen',
            name='buyer',
        ),
    ]
