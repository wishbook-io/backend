# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0234_categoryeavattribute_filterable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryeavattribute',
            name='is_required',
        ),
    ]
