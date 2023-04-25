# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0063_auto_20151226_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push_user_product',
            name='catalog',
            field=models.ForeignKey(related_name='pup_catalog', default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AlterField(
            model_name='push_user_product',
            name='selection',
            field=models.ForeignKey(related_name='pup_selection', default=None, blank=True, to='api.Selection', null=True),
        ),
    ]
