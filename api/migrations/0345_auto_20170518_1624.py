# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0344_auto_20170518_1145'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='brand',
            index_together=set([('company', 'id')]),
        ),
        migrations.AlterIndexTogether(
            name='company',
            index_together=set([('country', 'phone_number')]),
        ),
        migrations.AlterIndexTogether(
            name='companyuser',
            index_together=set([('company', 'deputed_to'), ('company', 'deputed_to', 'user')]),
        ),
    ]
