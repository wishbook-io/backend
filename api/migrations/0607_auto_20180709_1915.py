# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0606_shiprocketapilog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiprocketapilog',
            name='provider_invoice_url',
            field=models.URLField(max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiprocketapilog',
            name='provider_label_url',
            field=models.URLField(max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiprocketapilog',
            name='provider_manifest_url',
            field=models.URLField(max_length=250, null=True, blank=True),
        ),
    ]
