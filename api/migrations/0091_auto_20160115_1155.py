# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0090_auto_20160115_0954'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buyer',
            old_name='buyer_status',
            new_name='status',
        ),
    ]
