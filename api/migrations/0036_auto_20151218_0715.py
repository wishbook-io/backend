# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20151218_0647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='phone_number',
            field=models.CharField(max_length=13, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='branch',
            name='pincode',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
