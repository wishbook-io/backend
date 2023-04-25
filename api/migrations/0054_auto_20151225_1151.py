# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0053_auto_20151225_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(null=True, upload_to=b'brand_image/', blank=True),
        ),
    ]
