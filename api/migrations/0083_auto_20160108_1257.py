# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0082_auto_20160108_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagetest',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
