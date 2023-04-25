# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0251_auto_20161003_1834'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='company',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='push',
        ),
        migrations.RemoveField(
            model_name='invoicecredit',
            name='company',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
        migrations.DeleteModel(
            name='InvoiceCredit',
        ),
    ]
