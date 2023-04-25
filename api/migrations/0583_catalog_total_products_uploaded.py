# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0582_auto_20180529_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='total_products_uploaded',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
