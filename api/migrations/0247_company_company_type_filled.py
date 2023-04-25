# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0246_auto_20160929_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_type_filled',
            field=models.BooleanField(default=False),
        ),
    ]
