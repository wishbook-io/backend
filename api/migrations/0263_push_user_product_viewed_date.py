# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0262_auto_20161018_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user_product',
            name='viewed_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
