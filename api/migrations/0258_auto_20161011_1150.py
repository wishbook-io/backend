# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0257_auto_20161005_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicecredit',
            name='amount',
            field=models.IntegerField(),
        ),
    ]
