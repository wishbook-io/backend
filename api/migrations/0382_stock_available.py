# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0381_auto_20170711_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='available',
            field=models.IntegerField(default=0),
        ),
    ]
