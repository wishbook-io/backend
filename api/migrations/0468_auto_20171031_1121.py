# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0467_auto_20171031_1027'),
    ]

    operations = [
        migrations.RenameField(
            model_name='promotion',
            old_name='wholesaler_distributor',
            new_name='wholesaler',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='online_retailer_reseller',
        ),
    ]
