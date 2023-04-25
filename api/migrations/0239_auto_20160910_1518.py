# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0238_producteavflat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producteavflat',
            name='product',
            field=models.OneToOneField(to='api.Product'),
        ),
    ]
