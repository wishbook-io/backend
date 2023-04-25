# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0054_auto_20151225_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='image_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, null=True, editable=False, blank=True),
        ),
    ]
