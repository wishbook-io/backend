# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0580_auto_20180524_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketing',
            name='campaign_text',
            field=models.CharField(max_length=500),
        ),
    ]
