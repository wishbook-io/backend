# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0454_companybuyergroup_buyer_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companybuyergroup',
            unique_together=set([('company', 'buyer_type')]),
        ),
    ]
