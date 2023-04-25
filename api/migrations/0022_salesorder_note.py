# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20151208_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
    ]
