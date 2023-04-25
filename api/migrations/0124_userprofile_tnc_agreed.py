# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0123_auto_20160425_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='tnc_agreed',
            field=models.BooleanField(default=True),
        ),
    ]
