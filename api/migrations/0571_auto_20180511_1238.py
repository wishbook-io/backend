# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0570_auto_20180508_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 11, 7, 8, 13, 238155, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='story',
            name='deep_link',
            field=models.URLField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='story',
            name='is_disable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='story',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 11, 7, 8, 21, 797930, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='story',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='story',
            name='catalogs',
            field=models.ManyToManyField(to='api.Catalog', blank=True),
        ),
    ]
