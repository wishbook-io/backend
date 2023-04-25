# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_auto_20151225_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='thumbnail',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'catalog_image/'),
        ),
    ]
