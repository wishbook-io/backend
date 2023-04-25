# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0272_auto_20161206_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyuser',
            name='deputed_from',
            field=models.ForeignKey(default=None, blank=True, to='api.Company', null=True),
        ),
    ]
