# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0502_userreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreview',
            name='language',
            field=models.ManyToManyField(to='api.Language', blank=True),
        ),
    ]
