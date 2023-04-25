# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0241_auto_20160913_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='updatenotification',
            name='update_for',
            field=models.CharField(default=b'Android', max_length=30, choices=[(b'Android', b'Android'), (b'IOS', b'IOS')]),
        ),
    ]
