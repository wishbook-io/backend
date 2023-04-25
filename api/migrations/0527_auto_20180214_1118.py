# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0526_auto_20180214_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='platform',
            field=models.CharField(default='Android', max_length=100, choices=[(b'Android', b'Android'), (b'iOS', b'iOS')]),
            preserve_default=False,
        ),
    ]
