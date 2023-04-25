# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0411_auto_20170810_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companykyctaxation',
            name='company',
            field=models.OneToOneField(related_name='kyc', to='api.Company'),
        ),
    ]
