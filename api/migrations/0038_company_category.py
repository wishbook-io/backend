# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_remove_company_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='category',
            field=models.ManyToManyField(to='api.Category', blank=True),
        ),
    ]
