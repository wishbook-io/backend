# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0473_auto_20171102_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AlterField(
            model_name='push',
            name='change_price_add',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='push',
            name='change_price_fix',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='ship_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='api.Address', null=True),
        ),
    ]
