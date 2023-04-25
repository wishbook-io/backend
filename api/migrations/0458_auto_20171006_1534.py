# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0457_auto_20171006_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='expiry_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='catalog',
            name='supplier_disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='push',
            name='expiry_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='push_user',
            name='buyer_disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='push_user',
            name='expiry_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='push_user',
            name='supplier_disabled',
            field=models.BooleanField(default=False),
        ),
    ]
