# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_company_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='street_address',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
