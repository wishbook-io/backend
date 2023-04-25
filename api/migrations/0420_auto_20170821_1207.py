# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0419_wbcoupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='seller_discount',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='wb_coupon',
            field=models.ForeignKey(default=None, blank=True, to='api.WbCoupon', null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='wb_coupon_discount',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='wb_coupon',
            field=models.ForeignKey(default=None, blank=True, to='api.WbCoupon', null=True),
        ),
    ]
