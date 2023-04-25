# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_auto_20151229_0544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagetest',
            name='image_optional',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'images_test/', blank=True),
        ),
    ]
