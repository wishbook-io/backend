# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0096_auto_20160123_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selection',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='selection',
            unique_together=set([('name', 'user')]),
        ),
    ]
