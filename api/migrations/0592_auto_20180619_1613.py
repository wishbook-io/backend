# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0591_cartitem_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='processing_note',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='processing_note',
            field=models.TextField(null=True, blank=True),
        ),
    ]
