# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0100_auto_20160209_0603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesorder',
            name='screenshot',
        ),
        migrations.AddField(
            model_name='salesorder',
            name='purchase_image',
            field=models.ImageField(null=True, upload_to=b'order', blank=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='sales_image',
            field=models.ImageField(null=True, upload_to=b'order', blank=True),
        ),
    ]
