# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0482_auto_20171121_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='preffered_shipping_provider',
            field=models.CharField(default=b'Buyer Suggested', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')]),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='preffered_shipping_provider',
            field=models.CharField(default=b'Buyer Suggested', max_length=20, null=True, choices=[(b'WB Provided', b'WB Provided'), (b'Buyer Suggested', b'Buyer Suggested')]),
        ),
    ]
