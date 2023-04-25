# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0087_cataloglist_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='status',
        ),
        migrations.AddField(
            model_name='buyer',
            name='buyer_status',
            field=models.CharField(default=b'pending', max_length=20, choices=[(b'registrationpending', b'Registration Pending'), (b'pending', b'Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
    ]
