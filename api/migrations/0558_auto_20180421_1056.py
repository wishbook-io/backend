# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0557_sellerstatistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 15, 740391, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalogenquiry',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 21, 339649, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalogseller',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 23, 972504, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalogseller',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 26, 124458, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellerstatistic',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 27, 876507, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellerstatistic',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 30, 764431, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userplatforminfo',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 33, 140569, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userplatforminfo',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 21, 5, 26, 35, 380536, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sellerstatistic',
            name='catalogs_uploaded',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
