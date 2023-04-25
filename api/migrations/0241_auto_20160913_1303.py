# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0240_categoryeavattribute_is_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smstransaction',
            name='created_at',
            field=models.DateField(auto_now_add=True, unique=True),
        ),
    ]
