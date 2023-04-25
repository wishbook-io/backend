# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_registrationotp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='status',
            field=models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
    ]
