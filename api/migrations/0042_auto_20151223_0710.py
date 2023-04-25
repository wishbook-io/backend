# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_imagetest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagetest',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'image_test/', blank=True),
        ),
    ]
