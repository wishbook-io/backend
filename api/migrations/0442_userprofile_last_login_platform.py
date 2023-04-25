# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0441_auto_20170928_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_login_platform',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Lite', b'Lite'), (b'Android', b'Android'), (b'iOS', b'iOS'), (b'Webapp', b'Webapp')]),
        ),
    ]
