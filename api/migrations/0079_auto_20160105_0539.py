# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0078_brand_manufacturer_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='invitee_company',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
