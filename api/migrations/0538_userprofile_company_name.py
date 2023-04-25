# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0537_auto_20180319_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='company_name',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
    ]
