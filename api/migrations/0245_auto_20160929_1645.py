# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0244_auto_20160929_1643'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companytype',
            old_name='online_retailer',
            new_name='online_retailer_reseller',
        ),
        migrations.RenameField(
            model_name='companytype',
            old_name='wholesaler',
            new_name='wholesaler_distributor',
        ),
    ]
