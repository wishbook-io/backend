# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0296_product_public_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyproductflat',
            name='is_salable',
            field=models.BooleanField(default=False),
        ),
    ]
