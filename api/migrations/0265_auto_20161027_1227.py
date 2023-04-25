# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0264_auto_20161027_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryadjustment',
            name='remark',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
