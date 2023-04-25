# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_auto_20151225_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='thumbnail_ppoi',
        ),
        migrations.AlterField(
            model_name='company',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=b'company_image', blank=True),
        ),
    ]
