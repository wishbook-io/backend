# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0464_auto_20171016_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.ForeignKey(default=1, to='api.Country'),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
