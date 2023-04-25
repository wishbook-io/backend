# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0051_auto_20151225_0730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image_small',
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'product_image/'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False),
        ),
    ]
