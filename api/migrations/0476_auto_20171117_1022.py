# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0475_push_change_price_add_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='address',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='ship_to',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
    ]
