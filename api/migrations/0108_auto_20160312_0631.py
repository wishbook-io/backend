# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0107_push_to_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
