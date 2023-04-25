# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0231_product_mirror'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='purpose',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
