# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0196_inventoryadjustmentqty'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='skumap',
            unique_together=set([]),
        ),
    ]
