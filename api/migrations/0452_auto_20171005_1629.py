# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0451_paymentmethod'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companybuyergroup',
            unique_together=set([]),
        ),
    ]
