# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0577_auto_20180522_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditreference',
            name='transaction_on_credit',
            field=models.BooleanField(default=False),
        ),
    ]
