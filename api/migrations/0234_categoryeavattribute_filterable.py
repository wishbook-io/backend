# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0233_smstransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryeavattribute',
            name='filterable',
            field=models.BooleanField(default=False),
        ),
    ]
