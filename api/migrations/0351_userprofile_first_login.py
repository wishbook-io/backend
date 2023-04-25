# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0350_buyer_created_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='first_login',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
