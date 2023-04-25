# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0337_auto_20170429_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(blank=True, to='api.Invoice', null=True),
        ),
    ]
