# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0223_companyproductflat'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyproductflat',
            name='is_disable',
            field=models.BooleanField(default=False),
        ),
    ]
