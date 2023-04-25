# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0511_catalogeavflat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogeavflat',
            name='brand',
            field=models.ForeignKey(default=None, blank=True, to='api.Brand', null=True),
        ),
        migrations.AlterField(
            model_name='catalogeavflat',
            name='category',
            field=models.ForeignKey(default=None, blank=True, to='api.Category', null=True),
        ),
        migrations.AlterField(
            model_name='catalogeavflat',
            name='title',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
