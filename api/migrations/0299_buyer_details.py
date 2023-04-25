# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0298_buyer_buyer_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='details',
            field=models.TextField(null=True, blank=True),
        ),
    ]
