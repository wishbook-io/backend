# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0225_remove_companyproductflat_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyproductflat',
            name='push_reference',
            field=models.ForeignKey(default=None, blank=True, to='api.Push', null=True),
        ),
    ]
