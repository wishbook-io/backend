# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0448_auto_20171004_1744'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companybuyergroup',
            unique_together=set([('company', 'buyer_type')]),
        ),
    ]
