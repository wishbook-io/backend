# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0142_auto_20160518_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companybuyergroup',
            name='payment_duration',
            field=models.IntegerField(default=0),
        ),
    ]
