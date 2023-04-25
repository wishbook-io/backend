# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0076_auto_20160102_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(default=b'nonmanufacturer', max_length=20, choices=[(b'manufacturer', b'Manufacturer'), (b'nonmanufacturer', b'Non Manufacturer')]),
        ),
    ]
