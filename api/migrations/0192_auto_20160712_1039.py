# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0191_auto_20160711_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='seller_ref',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='order_number',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
