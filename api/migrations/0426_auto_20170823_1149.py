# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0425_auto_20170823_1133'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyrating',
            old_name='total_buyer_score',
            new_name='total_buyer_rating',
        ),
        migrations.RenameField(
            model_name='companyrating',
            old_name='total_seller_score',
            new_name='total_seller_rating',
        ),
    ]
