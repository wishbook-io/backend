# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_auto_20151225_0652'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='images_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'catalog_image/', blank=True),
        ),
    ]
