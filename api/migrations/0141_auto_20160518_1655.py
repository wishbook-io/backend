# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0140_auto_20160518_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyphonealias',
            name='alias_number',
            field=models.CharField(max_length=13),
        ),
    ]
