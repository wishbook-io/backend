# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0252_auto_20161005_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('billed_amount', models.PositiveIntegerField(null=True, blank=True)),
                ('balance_amount', models.PositiveIntegerField(null=True, blank=True)),
                ('discount', models.PositiveIntegerField(null=True, blank=True)),
                ('status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')])),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('item_type', models.CharField(max_length=200)),
                ('qty', models.PositiveIntegerField()),
                ('rate', models.PositiveIntegerField()),
                ('amount', models.PositiveIntegerField()),
                ('company', models.ForeignKey(to='api.Company')),
                ('invoice', models.ForeignKey(to='api.Invoice')),
            ],
        ),
    ]
