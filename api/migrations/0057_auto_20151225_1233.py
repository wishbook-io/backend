# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0056_auto_20151225_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='thumbnail_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='thumbnail',
            field=versatileimagefield.fields.VersatileImageField(null=True, upload_to=b'company_image/', blank=True),
        ),
    ]
