# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20151217_0513'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='buyersegmentation',
            unique_together=set([('segmentation_name', 'company')]),
        ),
    ]
