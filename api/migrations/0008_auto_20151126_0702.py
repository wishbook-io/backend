# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20151124_1157'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='branddistributor',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='branddistributor',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='branddistributor',
            name='company',
        ),
        migrations.DeleteModel(
            name='BrandDistributor',
        ),
    ]
