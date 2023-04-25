# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0206_catalog_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcode',
            name='barcode',
            field=models.CharField(unique=True, max_length=200),
        ),
    ]
