# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0383_auto_20170713_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='tranferred_to',
            field=models.ForeignKey(related_name='tranferred_order', blank=True, to='api.SalesOrder', null=True),
        ),
    ]
