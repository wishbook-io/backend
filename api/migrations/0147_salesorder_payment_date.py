# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0146_auto_20160519_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='payment_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
