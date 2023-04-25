# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0070_auto_20151230_0505'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user_product',
            name='sku',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]
