# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0355_salesorder_is_supplier_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorderitem',
            name='rate',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2),
        ),
    ]
