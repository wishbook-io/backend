# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0236_auto_20160908_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='buyer_approval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buyer',
            name='supplier_approval',
            field=models.BooleanField(default=False),
        ),
    ]
