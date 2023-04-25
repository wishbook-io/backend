# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0424_companyrating_orderrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyrating',
            name='total_buyer_score',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='companyrating',
            name='total_seller_score',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='companyrating',
            name='company',
            field=models.OneToOneField(to='api.Company'),
        ),
        migrations.AlterField(
            model_name='orderrating',
            name='order',
            field=models.OneToOneField(to='api.SalesOrder'),
        ),
    ]
