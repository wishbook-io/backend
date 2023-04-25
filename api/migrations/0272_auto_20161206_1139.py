# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0271_attendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='att_lat',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='att_long',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
