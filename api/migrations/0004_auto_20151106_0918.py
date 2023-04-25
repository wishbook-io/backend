# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20151106_0612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='street_address',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='company',
            name='street_address',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='product',
            name='fabric',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='work',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='order_number',
            field=models.CharField(max_length=50),
        ),
    ]
