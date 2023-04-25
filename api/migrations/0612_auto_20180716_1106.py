# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0611_auto_20180713_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketing',
            name='categories',
            field=models.ManyToManyField(related_name='marketings', to='api.Category', blank=True),
        ),
    ]
