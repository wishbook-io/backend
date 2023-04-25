# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0478_auto_20171117_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryadjustment',
            name='company',
            field=models.ForeignKey(default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='openingstock',
            name='company',
            field=models.ForeignKey(default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AlterField(
            model_name='inventoryadjustment',
            name='warehouse',
            field=models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True),
        ),
        migrations.AlterField(
            model_name='openingstock',
            name='warehouse',
            field=models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True),
        ),
    ]
