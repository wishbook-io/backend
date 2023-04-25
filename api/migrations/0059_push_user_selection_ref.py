# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0058_auto_20151225_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user',
            name='selection_ref',
            field=models.ForeignKey(related_name='push_user_selection_id', default=None, blank=True, to='api.Selection', null=True),
        ),
    ]
