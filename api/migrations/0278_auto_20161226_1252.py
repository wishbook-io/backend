# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0277_company_exp_push_delay'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='paytm_country',
            field=models.ForeignKey(default=1, to='api.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='paytm_phone_number',
            field=models.CharField(max_length=13, null=True, blank=True),
        ),
    ]
