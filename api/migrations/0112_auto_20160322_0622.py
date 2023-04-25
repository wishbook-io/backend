# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0111_auto_20160319_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='sms',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push',
            name='whatsapp',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
