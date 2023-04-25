# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0341_buyer_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push_user',
            name='total_price',
            field=models.DecimalField(max_digits=19, decimal_places=2, db_index=True),
        ),
    ]
