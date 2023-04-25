# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0386_warehouse_salesmen'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryadjustment',
            name='error_file',
            field=models.FileField(null=True, upload_to=b'adjustment_stock_error_file', blank=True),
        ),
        migrations.AddField(
            model_name='inventoryadjustment',
            name='upload_file',
            field=models.FileField(null=True, upload_to=b'adjustment_stock_upload_file', blank=True),
        ),
        migrations.AddField(
            model_name='openingstock',
            name='error_file',
            field=models.FileField(null=True, upload_to=b'opening_stock_error_file', blank=True),
        ),
        migrations.AddField(
            model_name='openingstock',
            name='upload_file',
            field=models.FileField(null=True, upload_to=b'opening_stock_upload_file', blank=True),
        ),
    ]
