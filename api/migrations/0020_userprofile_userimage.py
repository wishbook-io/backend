# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_company_brand_added_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='userimage',
            field=models.ImageField(null=True, upload_to=b'user_image', blank=True),
        ),
    ]
