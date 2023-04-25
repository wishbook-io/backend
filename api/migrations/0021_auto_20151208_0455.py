# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_userprofile_userimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='userimage',
            new_name='user_image',
        ),
    ]
