# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0522_remove_promotionalnotification_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionalnotification',
            name='app_version',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='deep_link',
            field=models.URLField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='last_login_platform',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Lite', b'Lite'), (b'Android', b'Android'), (b'iOS', b'iOS'), (b'Webapp', b'Webapp')]),
        ),
    ]
