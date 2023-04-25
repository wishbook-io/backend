# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0406_invoice_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionalnotification',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to=b'promotional_notification', blank=True),
        ),
    ]
