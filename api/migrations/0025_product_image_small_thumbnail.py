# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_brand_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_small_thumbnail',
            field=imagekit.models.fields.ProcessedImageField(default=1, upload_to=b'product_image'),
            preserve_default=False,
        ),
    ]
