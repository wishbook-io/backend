# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0486_promotion_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='total_catalog',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
