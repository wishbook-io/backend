# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0269_company_phone_number_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openingstockqty',
            name='opening_stock',
            field=models.ForeignKey(blank=True, to='api.OpeningStock', null=True),
        ),
    ]
