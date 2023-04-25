# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0072_auto_20160101_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='category',
            field=models.ManyToManyField(related_name='categories', to='api.Category', error_messages={b'blank': b'This list is required.'}),
        ),
    ]
