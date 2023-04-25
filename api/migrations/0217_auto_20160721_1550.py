# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0216_auto_20160721_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='category',
            field=models.ForeignKey(related_name='categories', default=12, to='api.Category'),
        ),
    ]
