# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0213_auto_20160720_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='catalog',
            field=models.ForeignKey(related_name='products', default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
