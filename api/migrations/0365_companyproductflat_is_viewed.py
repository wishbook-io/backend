# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0364_auto_20170629_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyproductflat',
            name='is_viewed',
            field=models.CharField(default=b'no', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
