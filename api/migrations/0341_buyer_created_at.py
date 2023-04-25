# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0340_companyuser_deputed_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2017, 5, 13, 5, 59, 19, 216583, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
