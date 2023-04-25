# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0243_buyersegmentation_applozic_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companytype',
            name='distributor',
        ),
        migrations.RemoveField(
            model_name='companytype',
            name='resellers',
        ),
        migrations.RemoveField(
            model_name='companytype',
            name='semi_wholesaler',
        ),
    ]
