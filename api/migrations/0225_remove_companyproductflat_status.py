# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0224_companyproductflat_is_disable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyproductflat',
            name='status',
        ),
    ]
