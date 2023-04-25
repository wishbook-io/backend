# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0145_auto_20160519_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='buyer_cancel',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='payment_details',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='supplier_cancel',
            field=models.TextField(null=True, blank=True),
        ),
    ]
