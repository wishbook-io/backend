# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0283_companyaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='purchase_reference_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='sales_reference_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
