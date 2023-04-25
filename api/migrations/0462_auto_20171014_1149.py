# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0461_auto_20171011_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='skumap',
            name='catalog',
            field=models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AddField(
            model_name='skumap',
            name='external_catalog',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='skumap',
            name='external_sku',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='skumap',
            name='product',
            field=models.ForeignKey(default=None, blank=True, to='api.Product', null=True),
        ),
    ]
