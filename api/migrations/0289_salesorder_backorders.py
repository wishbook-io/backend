# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0288_remove_salesorder_backorder_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='backorders',
            field=models.ManyToManyField(related_name='_backorders_+', to='api.SalesOrder', blank=True),
        ),
    ]
