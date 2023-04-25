# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0136_companyphonealias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyphonealias',
            name='status',
            field=models.CharField(default=b'Verification_Pending', max_length=30, choices=[(b'Verification_Pending', b'Verification Pending'), (b'Approved', b'Approved')]),
        ),
    ]
