# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20151203_0600'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='brand_added_flag',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
