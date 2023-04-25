# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0120_salesorder_traking_details'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesorder',
            old_name='traking_details',
            new_name='tracking_details',
        ),
    ]
