# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0565_jobs_action_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='order_type',
            field=models.CharField(default=b'Prepaid', max_length=20, choices=[(b'Prepaid', b'Prepaid'), (b'Credit', b'Credit')]),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='order_type',
            field=models.CharField(default=b'Prepaid', max_length=20, choices=[(b'Prepaid', b'Prepaid'), (b'Credit', b'Credit')]),
        ),
    ]
