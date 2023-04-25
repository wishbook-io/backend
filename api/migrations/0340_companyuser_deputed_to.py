# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0339_auto_20170503_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyuser',
            name='deputed_to',
            field=models.ForeignKey(related_name='deputed_to', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
