# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0279_push_exp_desp_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='sales_image_2',
            field=models.ImageField(null=True, upload_to=b'order', blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='sales_image_3',
            field=models.ImageField(null=True, upload_to=b'order', blank=True),
        ),
    ]
