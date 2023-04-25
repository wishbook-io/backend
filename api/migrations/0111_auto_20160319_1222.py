# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0110_auto_20160316_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='seller_company',
            field=models.ForeignKey(related_name='selling_order', to='api.Company'),
        ),
    ]
