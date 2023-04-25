# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0518_auto_20180119_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_password_set',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_approval_status',
            field=models.CharField(default=b'Approved', max_length=20, choices=[(b'Approved', b'Approved'), (b'Pending', b'Pending')]),
        ),
    ]
