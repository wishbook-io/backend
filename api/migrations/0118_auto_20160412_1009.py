# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0117_auto_20160401_1301'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companyuser',
            unique_together=set([]),
        ),
    ]
