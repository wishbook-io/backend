# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0455_auto_20171005_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='status',
            field=models.CharField(default=b'Enable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')]),
        ),
    ]
