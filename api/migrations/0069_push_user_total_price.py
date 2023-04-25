# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0068_auto_20151229_0615'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user',
            name='total_price',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=False,
        ),
    ]
