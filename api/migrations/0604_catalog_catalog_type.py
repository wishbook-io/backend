# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0603_auto_20180707_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='catalog_type',
            field=models.CharField(default=b'Catalog', max_length=30, choices=[(b'Catalog', b'Catalog'), (b'Non Catalog', b'Non Catalog')]),
        ),
    ]
