# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_salesorder_seller_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branddistributor',
            name='company',
            field=models.OneToOneField(to='api.Company'),
        ),
    ]
