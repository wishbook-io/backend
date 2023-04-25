# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0228_auto_20160811_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='mirror',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
