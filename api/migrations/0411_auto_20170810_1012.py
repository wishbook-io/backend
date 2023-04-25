# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0410_auto_20170809_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companykyctaxation',
            name='company',
            field=models.ForeignKey(related_name='kyc', to='api.Company'),
        ),
    ]
