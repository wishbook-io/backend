# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0581_auto_20180526_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brokeragepayment',
            name='payment_method',
            field=models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other'), (b'Wishbook Credit', b'Wishbook Credit'), (b'COD', b'COD')]),
        ),
        migrations.AlterField(
            model_name='cashbackrule',
            name='payment_status',
            field=models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Partially Paid', b'Partially Paid'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(default=b'Pending', max_length=20, choices=[(b'Pending', b'Pending'), (b'Partially Paid', b'Partially Paid'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='mode',
            field=models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other'), (b'Wishbook Credit', b'Wishbook Credit'), (b'COD', b'COD')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Partially Paid', b'Partially Paid'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled'), (b'Success', b'Success'), (b'Failure', b'Failure')]),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Pending', max_length=50, null=True, choices=[(b'Cart', b'Cart'), (b'Draft', b'Draft'), (b'COD Verification Pending', b'COD Verification Pending'), (b'Field Verification Pending', b'Field Verification Pending'), (b'Pending', b'Pending'), (b'Accepted', b'Accepted'), (b'In Progress', b'In Progress'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled'), (b'Closed', b'Closed'), (b'Buyer Cancelled', b'Buyer Cancelled')]),
        ),
        migrations.AlterField(
            model_name='salesorderauditlogentry',
            name='processing_status',
            field=models.CharField(default=b'Pending', max_length=50, null=True, choices=[(b'Cart', b'Cart'), (b'Draft', b'Draft'), (b'COD Verification Pending', b'COD Verification Pending'), (b'Field Verification Pending', b'Field Verification Pending'), (b'Pending', b'Pending'), (b'Accepted', b'Accepted'), (b'In Progress', b'In Progress'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled'), (b'Closed', b'Closed'), (b'Buyer Cancelled', b'Buyer Cancelled')]),
        ),
    ]
