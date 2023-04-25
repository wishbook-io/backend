# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0109_auto_20160316_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='company',
            field=models.ForeignKey(related_name='buying_order', to='api.Company'),
        ),
    ]
