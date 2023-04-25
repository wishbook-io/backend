# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0401_auto_20170801_1205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorytaxclass',
            name='tax_class',
        ),
        migrations.AddField(
            model_name='categorytaxclass',
            name='tax_classes',
            field=models.ManyToManyField(to='api.TaxClass'),
        ),
    ]
