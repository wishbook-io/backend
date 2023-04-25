# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0604_catalog_catalog_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='catalog_type',
            field=models.CharField(default=b'catalog', max_length=30, choices=[(b'catalog', b'catalog'), (b'noncatalog', b'noncatalog')]),
        ),
    ]
