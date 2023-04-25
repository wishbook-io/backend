# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0268_auto_20161027_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='phone_number_verified',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
