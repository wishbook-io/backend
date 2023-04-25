# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0300_auto_20170317_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishbookInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('billed_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('balance_amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('discount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
