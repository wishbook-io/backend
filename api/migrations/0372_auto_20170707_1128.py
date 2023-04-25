# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0371_buyersalesmen_salesmanlocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesmanlocation',
            name='city',
        ),
        migrations.AddField(
            model_name='salesmanlocation',
            name='city',
            field=models.ManyToManyField(to='api.City', blank=True),
        ),
        migrations.RemoveField(
            model_name='salesmanlocation',
            name='state',
        ),
        migrations.AddField(
            model_name='salesmanlocation',
            name='state',
            field=models.ManyToManyField(to='api.State', blank=True),
        ),
    ]
