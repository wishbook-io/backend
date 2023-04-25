# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0416_auto_20170811_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='mode',
            field=models.CharField(max_length=20, choices=[(b'NEFT', b'NEFT'), (b'Cheque', b'Cheque'), (b'PayTM', b'PayTM'), (b'Mobikwik', b'Mobikwik'), (b'Zaakpay', b'Zaakpay'), (b'Other', b'Other')]),
        ),
    ]
