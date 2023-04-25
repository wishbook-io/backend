# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0498_company_refered_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouptype',
            name='name',
            field=models.CharField(unique=True, max_length=20),
        ),
    ]
