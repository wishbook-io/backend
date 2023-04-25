# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0062_auto_20151226_0733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push_user',
            name='catalog',
            field=models.ForeignKey(related_name='push_user_catalog_id', default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AlterField(
            model_name='push_user',
            name='selection',
            field=models.ForeignKey(related_name='push_user_selection_id', default=None, blank=True, to='api.Selection', null=True),
        ),
    ]
