# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0201_buyer_warehouse'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='is_visible',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
