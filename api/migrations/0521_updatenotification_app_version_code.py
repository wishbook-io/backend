# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0520_buyer_supplier_person_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='updatenotification',
            name='app_version_code',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
