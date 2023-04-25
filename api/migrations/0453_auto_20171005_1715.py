# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0452_auto_20171005_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentmethod',
            old_name='payment_status',
            new_name='payment_type',
        ),
        migrations.RemoveField(
            model_name='companybuyergroup',
            name='buyer_type',
        ),
    ]
