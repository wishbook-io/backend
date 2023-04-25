# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0412_auto_20170810_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='transporter_courier',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='mode',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='tracking_number',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
