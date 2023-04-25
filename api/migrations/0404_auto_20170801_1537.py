# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0403_auto_20170801_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='taxes',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_amount',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True),
        ),
    ]
