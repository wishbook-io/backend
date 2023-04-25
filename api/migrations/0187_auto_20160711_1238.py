# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0186_appinstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
