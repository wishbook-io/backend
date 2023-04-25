# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0547_mobilestatemapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilestatemapping',
            name='mobile_no_start_with',
            field=models.CharField(unique=True, max_length=5),
        ),
    ]
