# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0133_auto_20160517_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='country',
            field=models.ForeignKey(related_name='branch_country', default=1, to='api.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.ForeignKey(related_name='company_country', default=1, to='api.Country'),
        ),
    ]
