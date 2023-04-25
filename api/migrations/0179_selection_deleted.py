# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0178_product_is_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
