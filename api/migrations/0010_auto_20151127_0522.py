# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_branddistributor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='view_permission',
            field=models.CharField(default=b'push', max_length=20, choices=[(b'public', b'Public'), (b'push', b'Push')]),
        ),
    ]
