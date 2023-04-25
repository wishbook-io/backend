# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0098_auto_20160204_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='group_type',
            field=models.CharField(default='wholesaler', max_length=20, choices=[(b'distributor', b'Distributor'), (b'wholesaler', b'Wholesaler'), (b'semi-wholesaler', b'Semi-Wholesaler'), (b'retailer', b'Retailer'), (b'online-retailer', b'Online Retailer'), (b'other', b'Other')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buyersegmentation',
            name='group_type',
            field=models.CharField(default='wholesaler', max_length=20, choices=[(b'distributor', b'Distributor'), (b'wholesaler', b'Wholesaler'), (b'semi-wholesaler', b'Semi-Wholesaler'), (b'retailer', b'Retailer'), (b'online-retailer', b'Online Retailer'), (b'other', b'Other')]),
            preserve_default=False,
        ),
    ]
