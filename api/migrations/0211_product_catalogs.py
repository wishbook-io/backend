# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0210_auto_20160719_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='catalogs',
            field=models.ForeignKey(related_name='product', default=None, blank=True, to='api.Catalog', null=True),
        ),
    ]
