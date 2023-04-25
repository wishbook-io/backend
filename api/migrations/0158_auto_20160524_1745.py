# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0157_companygroupflag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companygroupflag',
            name='company',
            field=models.OneToOneField(related_name='company_group_flag', to='api.Company'),
        ),
    ]
