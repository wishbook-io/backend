# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0613_userprofile_uninstall_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogeavflat',
            name='style',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
