# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_remove_imagetest_image_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagetest',
            name='image_optional',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'image_test/', blank=True),
        ),
    ]
