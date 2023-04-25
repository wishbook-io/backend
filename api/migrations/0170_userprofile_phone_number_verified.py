# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0169_company_newsletter_subscribe'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_number_verified',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
