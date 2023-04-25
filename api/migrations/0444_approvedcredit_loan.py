# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0443_auto_20171002_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovedCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lender_company', models.CharField(max_length=50, choices=[(b'Capital Float', b'Capital Float')])),
                ('total_limit', models.DecimalField(max_digits=19, decimal_places=2)),
                ('minimum_order_value', models.DecimalField(max_digits=19, decimal_places=2)),
                ('used_limit', models.DecimalField(max_digits=19, decimal_places=2)),
                ('available_limit', models.DecimalField(max_digits=19, decimal_places=2)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=50, choices=[(b'Pending', b'Pending'), (b'Processed', b'Processed'), (b'Repaid', b'Repaid'), (b'Canceled', b'Canceled')])),
                ('approved_credit', models.ForeignKey(to='api.ApprovedCredit')),
                ('company', models.ForeignKey(to='api.Company')),
                ('order', models.ForeignKey(to='api.SalesOrder')),
            ],
        ),
    ]
