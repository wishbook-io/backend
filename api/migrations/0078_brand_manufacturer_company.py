# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0077_auto_20160102_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='manufacturer_company',
            field=models.ForeignKey(related_name='manufacturer_brand', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
