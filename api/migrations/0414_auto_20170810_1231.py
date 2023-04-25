# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0413_auto_20170810_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 10, 7, 1, 57, 261243, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(related_name='payments', default=None, blank=True, to='api.Invoice', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_reference',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='state',
            name='state_type',
            field=models.CharField(default=b'STATE', max_length=10, choices=[(b'STATE', b'STATE'), (b'UT', b'UT')]),
        ),
    ]
