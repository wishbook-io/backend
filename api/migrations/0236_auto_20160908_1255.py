# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0235_remove_categoryeavattribute_is_required'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='categoryeavattribute',
            unique_together=set([('category', 'attribute')]),
        ),
    ]
