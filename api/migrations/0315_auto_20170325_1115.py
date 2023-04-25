# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0314_auto_20170325_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorderitem',
            name='canceled_qty',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='salesorderitem',
            name='dispatched_qty',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='salesorderitem',
            name='invoiced_qty',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
