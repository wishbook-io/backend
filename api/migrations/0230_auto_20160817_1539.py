# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0229_catalog_mirror'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='mirror',
            field=models.ForeignKey(related_name='catalog_mirror', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
