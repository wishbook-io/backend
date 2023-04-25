# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0230_auto_20160817_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='mirror',
            field=models.ForeignKey(related_name='product_mirror', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='api.Product', null=True),
        ),
    ]
