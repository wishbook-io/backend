# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0304_auto_20170320_1725'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishbookInvoicePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('invoice', models.ForeignKey(to='api.WishbookInvoice')),
                ('payment', models.ForeignKey(to='api.WishbookPayment')),
            ],
        ),
    ]
