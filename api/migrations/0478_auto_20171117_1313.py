# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0477_auto_20171117_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='warehouse',
            field=models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True),
        ),
    ]
