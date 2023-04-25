# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0245_auto_20160929_1645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companytype',
            old_name='agents',
            new_name='broker',
        ),
    ]
