# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0059_push_user_selection_ref'),
    ]

    operations = [
        migrations.RenameField(
            model_name='push_user',
            old_name='selection_ref',
            new_name='selection',
        ),
        migrations.AddField(
            model_name='push_user',
            name='catalog',
            field=models.ForeignKey(related_name='push_user_catalog_id', default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
