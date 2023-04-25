# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0485_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='language',
            field=models.ManyToManyField(to='api.Language', blank=True),
        ),
    ]
