# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20151215_0744'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='image',
            field=models.ImageField(null=True, upload_to=b'brand_image', blank=True),
        ),
    ]
