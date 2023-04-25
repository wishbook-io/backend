# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0519_auto_20180120_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='supplier_person_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
