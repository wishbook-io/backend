# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0208_auto_20160718_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='categories',
            field=models.ForeignKey(default=12, to='api.Category'),
        ),
    ]
