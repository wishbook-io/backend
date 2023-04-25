# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0239_auto_20160910_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryeavattribute',
            name='is_required',
            field=models.BooleanField(default=False),
        ),
    ]
