# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0615_auto_20180725_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='transaction_type',
            field=models.CharField(default=b'Sale Purchase', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')]),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='transaction_type',
            field=models.CharField(default=b'Sale Purchase', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')]),
        ),
        migrations.AlterField(
            model_name='salesorderauditlogentry',
            name='transaction_type',
            field=models.CharField(default=b'Sale Purchase', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')]),
        ),
    ]
