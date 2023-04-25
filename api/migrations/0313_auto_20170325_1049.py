# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0312_auto_20170323_1215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credit',
            name='company',
        ),
        migrations.RemoveField(
            model_name='invoicecredit',
            name='credit',
        ),
        migrations.RemoveField(
            model_name='invoicecredit',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='invoicepayment',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='invoicepayment',
            name='payment',
        ),
        migrations.DeleteModel(
            name='Credit',
        ),
        migrations.DeleteModel(
            name='InvoiceCredit',
        ),
        migrations.DeleteModel(
            name='InvoicePayment',
        ),
    ]
