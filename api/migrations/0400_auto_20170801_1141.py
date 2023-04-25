# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0399_auto_20170731_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cataloguploadoption',
            name='catalog',
            field=models.OneToOneField(to='api.Catalog'),
        ),
    ]
