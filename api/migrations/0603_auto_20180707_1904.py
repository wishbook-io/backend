# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0602_auto_20180707_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companybankdetails',
            name='account_name',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='companybankdetails',
            name='account_number',
            field=models.BigIntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='companybankdetails',
            name='account_type',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Savings', b'Savings'), (b'Current', b'Current')]),
        ),
        migrations.AlterField(
            model_name='companybankdetails',
            name='bank_name',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='companybankdetails',
            name='ifsc_code',
            field=models.CharField(default=None, max_length=20, null=True, blank=True),
        ),
    ]
