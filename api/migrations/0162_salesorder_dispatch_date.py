# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0161_auto_20160526_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='dispatch_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
