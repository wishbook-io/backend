# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0548_auto_20180406_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'category_images/', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_home_display',
            field=models.BooleanField(default=False),
        ),
    ]
