# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0089_auto_20160115_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='relationship_type',
            field=models.CharField(default=b'None', max_length=20, choices=[(b'buyer', b'Buyer'), (b'supplier', b'Supplier'), (b'salesperson', b'Salesperson'), (b'administrator', b'Administrator')]),
        ),
    ]
