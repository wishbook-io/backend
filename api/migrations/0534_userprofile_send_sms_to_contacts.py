# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0533_auto_20180310_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='send_sms_to_contacts',
            field=models.BooleanField(default=True),
        ),
    ]
