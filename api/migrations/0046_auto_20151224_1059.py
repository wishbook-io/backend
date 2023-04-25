# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_imagetest_image_optional'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagetest',
            name='image',
        ),
        migrations.RemoveField(
            model_name='imagetest',
            name='image_ppoi',
        ),
        migrations.AddField(
            model_name='imagetest',
            name='images',
            field=versatileimagefield.fields.VersatileImageField(default=1, upload_to=b'images_test/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imagetest',
            name='images_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False),
        ),
    ]
