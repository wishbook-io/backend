# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0453_auto_20171005_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='companybuyergroup',
            name='buyer_type',
            field=models.CharField(default='Broker', max_length=50, choices=[(b'Wholesaler', b'Wholesaler'), (b'Retailer', b'Retailer'), (b'Broker', b'Broker'), (b'Public', b'Public')]),
            preserve_default=False,
        ),
    ]
