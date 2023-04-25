# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0480_auto_20171118_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producteavflat',
            name='catalog',
            field=models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AlterField(
            model_name='producteavflat',
            name='category',
            field=models.ForeignKey(default=None, blank=True, to='api.Category', null=True),
        ),
    ]
