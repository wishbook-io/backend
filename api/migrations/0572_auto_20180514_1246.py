# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0571_auto_20180511_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='visible_to_buyer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='visible_to_supplier',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='visible_to_buyer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='visible_to_supplier',
            field=models.BooleanField(default=True),
        ),
    ]
