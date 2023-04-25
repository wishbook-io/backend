# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0597_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbackrule',
            name='payment_type',
            field=models.CharField(max_length=50, choices=[(b'Online', b'Online'), (b'Offline', b'Offline'), (b'Credit', b'Credit'), (b'Cash on Delivery', b'Cash on Delivery'), (b'Credit line', b'Credit line')]),
        ),
        migrations.AlterField(
            model_name='companycreditaprovedline',
            name='company',
            field=models.ForeignKey(related_name='credit_line', to='api.Company'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='payment_type',
            field=models.CharField(max_length=50, choices=[(b'Online', b'Online'), (b'Offline', b'Offline'), (b'Credit', b'Credit'), (b'Cash on Delivery', b'Cash on Delivery'), (b'Credit line', b'Credit line')]),
        ),
    ]
