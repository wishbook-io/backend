# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0354_auto_20170602_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='is_supplier_approved',
            field=models.BooleanField(default=True),
        ),
    ]
