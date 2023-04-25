# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0219_auto_20160729_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='single_company_push',
            field=models.ForeignKey(related_name='single_push', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
