# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0348_auto_20170519_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(related_name='items', blank=True, to='api.Invoice', null=True),
        ),
    ]
