# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0600_auto_20180703_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyBankDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_name', models.CharField(max_length=100)),
                ('account_number', models.BigIntegerField()),
                ('bank_name', models.CharField(max_length=100)),
                ('ifsc_code', models.CharField(max_length=20)),
                ('account_type', models.CharField(max_length=20, choices=[(b'Savings', b'Savings'), (b'Current', b'Current')])),
                ('company', models.OneToOneField(related_name='bankdetail', to='api.Company')),
            ],
        ),
    ]
