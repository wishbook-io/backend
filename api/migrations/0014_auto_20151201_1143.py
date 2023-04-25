# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_company_company_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(default=b'notmanufacture', max_length=20, choices=[(b'manufacture', b'Manufacture'), (b'notmanufacture', b'Not Manufacture')]),
        ),
    ]
