# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0550_auto_20180412_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='transaction_type',
            field=models.CharField(default=b'Marketplace', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')]),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='cancelled_by',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Buyer', b'Buyer'), (b'Seller', b'Seller')]),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='seller_cancellation_reason',
            field=models.CharField(default=None, max_length=30, null=True, blank=True, choices=[(b'Not In Stock', b'Not In Stock'), (b'Credit', b'Credit'), (b'Other', b'Other')]),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='transaction_type',
            field=models.CharField(default=b'Marketplace', max_length=50, choices=[(b'Sale Purchase', b'Sale Purchase'), (b'Marketplace', b'Marketplace')]),
        ),
    ]
