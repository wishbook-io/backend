# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_push_user_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user_product',
            name='catalog',
            field=models.ForeignKey(related_name='pup_catalog', default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='selection',
            field=models.ForeignKey(related_name='pup_selection', default=None, blank=True, to='api.Selection', null=True),
        ),
    ]
