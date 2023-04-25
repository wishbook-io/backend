# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0294_auto_20170302_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyproductflat',
            name='is_salable',
            field=models.BooleanField(default=True),
        ),
    ]
