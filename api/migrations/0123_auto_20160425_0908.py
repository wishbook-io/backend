# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0122_auto_20160422_1213'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={},
        ),
        migrations.AlterModelOptions(
            name='catalog',
            options={},
        ),
        migrations.AlterModelOptions(
            name='company',
            options={},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={},
        ),
        migrations.AlterModelOptions(
            name='salesorder',
            options={},
        ),
        migrations.AlterModelOptions(
            name='selection',
            options={},
        ),
        migrations.AlterModelOptions(
            name='usernumber',
            options={},
        ),
        migrations.AddField(
            model_name='registrationotp',
            name='is_verified',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
